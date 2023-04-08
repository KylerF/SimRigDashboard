'''
Defines static GraphQL queries and subscriptions for the iRacing GraphQL API.
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
    subscription IracingData {
        iracing {
            Speed
            RPM
            Gear
        }
    }
    '''
)
