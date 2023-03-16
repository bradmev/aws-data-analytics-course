#!/usr/bin/env python
from constructs import Construct

from cdktf import TerraformOutput, RemoteBackend, TerraformAsset, AssetType, Resource

from imports.aws.s3_bucket import S3Bucket
from imports.aws.s3_object import S3Object

from imports.aws.iam_policy import IamPolicy
from imports.aws.iam_role import IamRole
from imports.aws.iam_policy_attachment import IamPolicyAttachment
from imports.aws.iam_role_policy_attachment import IamRolePolicyAttachment

from imports.aws.kinesis_firehose_delivery_stream import (
    KinesisFirehoseDeliveryStream,
    KinesisFirehoseDeliveryStreamExtendedS3Configuration,
)


from lib.EnvironmentOptions import EnvironmentOptions

import json


class FirehoseOptions:
    def __init__(
        self,
        name: str,
    ) -> None:
        self.name = name


class CustomFirehose(Resource):
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {"Service": "firehose.amazonaws.com"},
                "Effect": "Allow",
                "Sid": "",
            }
        ],
    }

    def __init__(
        self,
        scope: Construct,
        id: str,
        options: EnvironmentOptions,
        firehose_options: FirehoseOptions,
    ):
        self.firehose_options = firehose_options
        self.options = options
        super().__init__(scope, id)

        # create bucket to store firehose output
        firehose_bucket = S3Bucket(
            self, "bucket", bucket_prefix=f"{options.env}-firehose"
        )

        # create policy content
        s3_delivery_policy_content = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:AbortMultipartUpload",
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:PutObject",
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{firehose_bucket.bucket}",
                        f"arn:aws:s3:::{firehose_bucket.bucket}/*",
                    ],
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "kinesis:DescribeStream",
                        "kinesis:GetShardIterator",
                        "kinesis:GetRecords",
                        "kinesis:ListShards",
                    ],
                    "Resource": f"arn:aws:kinesis:{self.options.region}:{self.options.account_id}:stream/{self.firehose_options.name}",
                },
            ],
        }

        # orig
        # "Resource": f"arn:aws:kinesis:{self.options.region}:{self.options.account_id}:stream/{self.firehose_options.name}",
        # test
        # "Resource": f"arn:aws:firehose:{self.options.region}:{self.options.account_id}:deliverystream/{self.firehose_options.name}",

        s3_delivery_policy = IamPolicy(
            self,
            "iam-delivery-policy",
            policy=json.dumps(s3_delivery_policy_content, indent=4),
        )

        # create role with policy and assume role policy
        s3_firehose_delivery_role = IamRole(
            self,
            "firehose-role",
            name=f"{self.firehose_options.name}-role",
            assume_role_policy=json.dumps(self.assume_role_policy, indent=4),
            managed_policy_arns=[s3_delivery_policy.arn],
        )

        s3_config = KinesisFirehoseDeliveryStreamExtendedS3Configuration(
            role_arn=s3_firehose_delivery_role.arn,
            bucket_arn=firehose_bucket.arn,
            buffer_size=64,
            dynamic_partitioning_configuration={"enabled": False},
            buffer_interval=60,
        )

        self.firehose = KinesisFirehoseDeliveryStream(
            self,
            "firehose",
            name=self.firehose_options.name,
            destination="extended_s3",
            extended_s3_configuration=s3_config,
        )
