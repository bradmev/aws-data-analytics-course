#!/usr/bin/env python
from constructs import Construct
from cdktf import Resource

from imports.aws.dynamodb_table import (
    DynamodbTable,
    DynamodbTableConfig,
    DynamodbTableAttribute,
)

from lib.EnvironmentOptions import EnvironmentOptions


class DynamoDBTableOptions:
    def __init__(
        self,
        name: str,
    ) -> None:
        self.name = name


class CustomDynamoDBTable(Resource):
    def __init__(
        self,
        scope: Construct,
        id: str,
        # options: EnvironmentOptions,
        table_options: DynamoDBTableOptions,
    ):
        self.table_options = table_options
        super().__init__(scope, id)

        self.table = DynamodbTable(
            self,
            id,
            name=self.table_options.name,
            attribute=[
                DynamodbTableAttribute(name="CustomerId", type="N"),
                DynamodbTableAttribute(name="OrderId", type="S"),
            ],
            hash_key="CustomerId",
            write_capacity=5,
            read_capacity=5,
            range_key="OrderId",
        )
