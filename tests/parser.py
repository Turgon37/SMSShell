#!/usr/bin/python3

import os
import subprocess
import sys

env1 = dict(
    SMS_MESSAGES="1",
    DECODED_PARTS="0",
    SMS_1_NUMBER="0124",
    SMS_1_CLASS="-1",
    SMS_1_TEXT="ghgg",
)

env2 = dict(
    SMS_2_CLASS="-1",
    SMS_MESSAGES="3",
    DECODED_PARTS="1",
    SMS_3_NUMBER="0124",
    SMS_3_TEXT="ernvgigfhhykfkkfdknxdhkjxhkkckjghfkbfujvjjxtyfjcuhdy8hdyujftucdyjxyhfyhrijfiigujugkcjtfdskfgjhfyhffyernvgi",
    SMS_2_TEXT="cuhdy8hdyujftucdyjxyhfyhrijfiigujugkcjtfdskfgjhfyhffyernvgigfhhykfkkfdknxdhkjxhkkckjghfkbfujvjjxtyfjcuhdy8hdyujftucdyjxyhfyhrijfiigujugkcjtfdskfgjhfyhffy",
    SMS_2_NUMBER="0124",
    SMS_3_CLASS="-1",
    DECODED_0_TEXT="ijhgfhhykfkkfdknxdhkjxhkkckjghfkbfujvjjxtyfjcuhdy8hdyujftucdyjxyhfyhrijfiigujugkcjtfdskfgjhfyhffyernvgifoxhidtuhgfhhykfkkfdknxdhkjxhkkckjghfkbfujvjjxtyfjcuhdy8hdyujftucdyjxyhfyhrijfiigujugkcjtfdskfgjhfyhffyernvgigfhhykfkkfdknxdhkjxhkkckjghfkbfujvjjxtyfjcuhdy8hdyujftucdyjxyhfyhrijfiigujugkcjtfdskfgjhfyhffyernvgigfhhykfkkfdknxdhkjxhkkckjghfkbfujvjjxtyfjcuhdy8hdyujftucdyjxyhfyhrijfiigujugkcjtfdskfgjhfyhffyernvgi",
    SMS_1_NUMBER="0124",
    SMS_1_CLASS="-1",
    SMS_1_TEXT="ijhgfhhykfkkfdknxdhkjxhkkckjghfkbfujvjjxtyfjcuhdy8hdyujftucdyjxyhfyhrijfiigujugkcjtfdskfgjhfyhffyernvgifoxhidtuhgfhhykfkkfdknxdhkjxhkkckjghfkbfujvjjxtyfj"
)

env = env2

for key in env:
  os.environ[key] = env[key]

subprocess.call(['../bin/sms-shell-parser'], stdout=sys.stdout)
