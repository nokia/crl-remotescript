# Copyright (C) 2019, Nokia

*** Setting ***
Library     RemoteScript

*** Variable ***

*** Test Case ***
Execute 1
        Set Target              localhost                                   root    root    default     telnet
        Set Target Property     default     port                            2323
        Set Target Property     default     login timeout                   2
        Set Target Property     default     max connection attempts         3
        Run Keyword And Expect Error        *       Execute Command In Target       Hello World

Execute 2
        Set Target              localhost                                   root    root    default     telnet
        Set Target Property     default     port                            2323
        Set Target Property     default     login timeout                   2
        Set Target Property     default     max connection attempts         3
        Set Target Property     default     connection failure is error     False
        ${props}                Get Target Properties                       default
        Log                     ${props}
        ${result}               Execute Command In Target                   Hello World
        Log                     ${result}
        Should Be Equal False   ${result.connection_ok}

