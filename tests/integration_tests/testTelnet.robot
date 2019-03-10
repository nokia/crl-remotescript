# Copyright (C) 2019, Nokia

*** Setting ***
Library     RemoteScript

*** Test Case ***
Execute1
        [Tags]                  DEFAULT_PROMPT
        Set Target              localhost       root    root    default     telnet
        Set Target Property     default         port    2323
        Set Target Property     default         login timeout   5
        Set Target Property     default         connection break is error       False
        ${result}               Execute Command In Target       Hello World

Execute2
        [Tags]                  REGEXP_PROMPT
        Set Target              localhost                               root    root    default     telnet
        Set Target Property     default     port                        2323
        Set Target Property     default     login timeout               5
        Set Target Property     default     prompt                      \$|~${SPACE}
        Set Target Property     default     prompt is regexp            True
        Set Target Property     default     connection break is error   False
        ${result}               Execute Command In Target               Hello World

Execute3
        [Tags]                          FOOBAR_PROMPT
        Set Target                      localhost           root    root    default     telnet
        Set Default Target Property     port                2323
        Set Default Target Property     login prompt        foo:${SPACE}
        Set Default Target Property     password prompt     bar:${SPACE}
        Set Default Target Property     login timeout       5
        Set Target Property             default             connection break is error       False
        ${result}                       Execute Command In Target       Hello World

