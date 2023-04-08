'''
Defines static GraphQL queries and subscriptions for the SimRig GraphQL API.
'''
from gql import gql

# Active driver subscription
active_driver_query = gql(
    '''
    subscription ActiveDriver {
        activeDriver {
            name
            nickname
        }
    }
    '''
)

# Specify desired iRacing data variables in this query
iracing_query = gql(
    '''
    subscription IracingData($fps: Int) {
        iracing(fps: $fps) {
            Speed
            RPM
            Gear
        }
    }
    '''
)
