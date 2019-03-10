# Copyright (C) 2019, Nokia

*** Setting ***
Test Setup      Initialize Targets
Library         RemoteScript
Resource        resource.robot

*** Test Case ***
Timeout
        Run Keyword And Expect Error    *timed out*     Execute Command In Target       sleep 60        default     fg      3

Bg Timeout
        Execute Background Command In Target    sleep 60        default                         bg
        Execute Command In Target               sleep 2         default                         fg      15
        Run Keyword And Expect Error            *timed out*     Wait Background Execution       bg      3

Script Timeout
        Run Keyword And Expect Error    *timed out*     Execute Script In Target        sleep.sh        default     fg      3

Bg Script Timeout
        Execute Background Script In Target     sleep.sh        default                         bg
        Execute Command In Target               sleep 2         default                         fg      15
        Run Keyword And Expect Error            *timed out*     Wait Background Execution       bg      3

