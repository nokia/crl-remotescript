# Copyright (C) 2019, Nokia


*** Setting ***
Library     RemoteScript

*** Variable ***

*** Test Case ***
No Target
    Run Keyword And Expect Error    *Unknown target: "default"*
    ...    Execute Command In Target    Hello World
