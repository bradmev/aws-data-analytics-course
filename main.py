#!/usr/bin/env python
import os
from constructs import Construct
from cdktf import App, TerraformStack, TerraformVariable, Token
from imports.aws.provider import AwsProvider
from lib.EnvironmentOptions import EnvironmentOptions

from section_two.SectionTwo import SectionTwo
from section_three.SectionThree import SectionThree
from section_four.SectionFour import SectionFour, SectionFourOptions


class MyCourseStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        self.environment_opts = EnvironmentOptions(
            region=os.environ["REGION"],
            env=os.environ["ENV"],
            account_id=os.environ["ACCOUNT_ID"],
            key_pair_name=os.environ["KEY_PAIR_NAME"],
        )

        AwsProvider(self, "aws-provider", region=self.environment_opts.region)

        SectionTwo(self, "section-one", options=self.environment_opts)

        section_three = SectionThree(self, "section-two", options=self.environment_opts)

        section_four = SectionFour(
            self,
            "section-four",
            options=self.environment_opts,
            section_options=SectionFourOptions(
                table_arn=section_three.dynamodb_table.table.arn,
            ),
        )


app = App()
MyCourseStack(app, "aws-data-analytics-course")

app.synth()
