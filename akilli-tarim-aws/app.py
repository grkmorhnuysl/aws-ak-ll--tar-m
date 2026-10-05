#!/usr/bin/env python3
import os
import aws_cdk as cdk
from akilli_tarim_aws.akilli_tarim_aws_stack import AkilliTarimAwsStack

app = cdk.App()

# Mimariyi ayağa kaldıran sınıfımızı çağırıyoruz
AkilliTarimAwsStack(app, "AkilliTarimAwsStack")

# İŞTE EKSİK OLAN SİHİRLİ KOMUT: Bulut şablonunu oluştur!
app.synth()