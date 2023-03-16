from cdktf import Resource, Token, Fn
from constructs import Construct
from lib.EnvironmentOptions import EnvironmentOptions
from lib.CustomDynamoDBTable import CustomDynamoDBTable, DynamoDBTableOptions


class SectionThree(Resource):
    def __init__(self, scope: Construct, id: str, options: EnvironmentOptions):
        self.options = options
        super().__init__(scope, id)

        self.dynamodb_table = CustomDynamoDBTable(
            self, "table", table_options=DynamoDBTableOptions(name="CadabraOrders")
        )
