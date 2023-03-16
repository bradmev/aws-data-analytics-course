from cdktf import Resource, Token, Fn, TerraformOutput
from constructs import Construct
from lib.EnvironmentOptions import EnvironmentOptions
from lib.CustomDynamoDBTable import CustomDynamoDBTable, DynamoDBTableOptions

from lib.CustomLambda import CustomLambda, LambdaOptions


class SectionFourOptions:
    def __init__(
        self,
        table_arn: str,
    ) -> None:
        self.table_arn = table_arn


class SectionFour(Resource):
    def __init__(
        self,
        scope: Construct,
        id: str,
        options: EnvironmentOptions,
        section_options: SectionFourOptions,
    ):
        self.options = options
        self.section_options = section_options
        super().__init__(scope, id)

        lambda_opts = LambdaOptions(
            name="ProcessOrders",
            asset_path="section_four/consumer_fn",
            version="3",
            handler="index.lambda_handler",
            runtime="python3.9",
            stage="dev",
            lambda_role_polices=[
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
                "arn:aws:iam::aws:policy/AmazonKinesisReadOnlyAccess",
                "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
            ],
            event_mapping_arn=self.section_options.table_arn,
        )

        custom_lambda = CustomLambda(
            self, "lambda", self.options, lambda_options=lambda_opts
        )

        TerraformOutput(self, "lambda_id", value=custom_lambda.lambda_function.arn)
        print(custom_lambda.lambda_function.arn)
