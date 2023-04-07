from gql.transport.websockets import WebsocketsTransport
from gql.transport.exceptions import TransportQueryError
from gql import gql, Client
import logging
import asyncio
import backoff

# Configure application logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Disable transport level debug logs from gql and asyncio
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('gql').setLevel(logging.WARNING)

# Configure GraphQL connection for subscriptions
ws_transport = WebsocketsTransport(url='ws://localhost:8000/graphql')
ws_client = Client(
    transport=ws_transport,
)

# Active driver subscription
active_driver_query = gql(
    '''
    subscription ActiveDriver {
        activeDriver {
            id
            name
            nickname
            profilePic
        }
    }
    '''
)

# Specify desired iRacing data variables in this query
iracing_query = gql(
    '''
    subscription IracingData {
        iracing {
            Speed
            RPM
            Gear
        }
    }
    '''
)

async def iracing_subscription(session):
    '''
    Results are returned each time a new iRacing data frame is available (30 FPS
    or framerate specified in subscription query)
    '''
    log.info('Subscribing to iRacing data')

    try:
        async for result in session.subscribe(iracing_query):
            log.debug(f'iRacing: {result}')
    except TransportQueryError:
        log.error(
            'Query validation error. Ensure that variables in IracingDataFrame'
            'are correctly typed.'
        )
        return

async def active_driver_subscription(session):
    '''
    Start listening for active driver changes
    '''
    log.info('Subscribing to active driver')

    try:
        async for result in session.subscribe(active_driver_query):
            log.debug(f'Active driver: {result}')  
    except TransportQueryError:
        log.error(
            'Query validation error. Ensure that variables in ActiveDriver'
            'are correctly typed.'
        )
        return

@backoff.on_exception(backoff.expo, Exception, max_time=300)
async def get_iracing_data():
    '''
    Gathers all of the above query functions into tasks
    '''
    async with ws_client as session:
        iracing_task = asyncio.create_task(
            iracing_subscription(session)
        )
        active_driver_task = asyncio.create_task(
            active_driver_subscription(session)
        )
        await asyncio.gather(iracing_task, active_driver_task)

############################################################
# Run all tasks until complete
asyncio.run(get_iracing_data())
