'''
Subscribes to GraphQL subscriptions and updates a dictionary with the latest
data.
'''
from gql.transport.websockets import WebsocketsTransport
from gql.transport.exceptions import TransportQueryError
from dotenv import dotenv_values
from gql import Client
import logging
import asyncio
import backoff

from queries import active_driver_query, iracing_query

config = dotenv_values(".env")

# Configure application logging
logging.basicConfig(level=config.get('LOG_LEVEL', 'INFO'))
log = logging.getLogger(__name__)

# Disable transport level debug logs from gql and asyncio
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('gql').setLevel(logging.WARNING)

# Configure GraphQL connection for subscriptions
ws_transport = WebsocketsTransport(url=f'ws://{config.get("API_HOST", "localhost")}:{config.get("API_PORT", 8000)}/graphql')
ws_client = Client(
    transport=ws_transport,
)

event_loop = asyncio.get_event_loop()

# Dictionary containing up-to-date iRacing and active driver data
data = {
    'iracing': {
        'Speed': 0,
        'RPM': 0,
        'Gear': 0,
    },
    'active_driver': {
        'id': 0,
        'name': '',
        'nickname': '',
        'profilePic': '',
    },
}

def update_iracing_data(new_data):
    '''
    Update iRacing data dictionary with new values
    '''
    data['iracing'] = new_data

def update_active_driver(new_data):
    '''
    Update active driver data dictionary with new values
    '''
    data['active_driver'] = new_data

async def iracing_subscription(session):
    '''
    Results are returned each time a new iRacing data frame is available (30 FPS
    or framerate specified in subscription query)
    '''
    log.info('Subscribing to iRacing data')

    try:
        async for result in session.subscribe(iracing_query):
            log.debug(f'iRacing: {result}')
            update_iracing_data(result['iracing'])
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
            update_active_driver(result['activeDriver'])
    except TransportQueryError:
        log.error(
            'Query validation error. Ensure that variables in ActiveDriver'
            'are correctly typed.'
        )
        return

@backoff.on_exception(backoff.expo, Exception, max_time=300)
async def subscribe_to_data():
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

def start():
    '''
    Starts the asyncio event loop
    '''
    event_loop.run_until_complete(subscribe_to_data())

def stop():
    '''
    Stops the asyncio event loop
    '''
    event_loop.stop()

if __name__ == '__main__':
    start()
