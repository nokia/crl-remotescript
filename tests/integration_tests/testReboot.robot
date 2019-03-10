# Copyright (C) 2019, Nokia

*** Setting ***
Test Setup      Initialize Targets
Library         RemoteScript
Resource        resource.robot

*** Variable ***

*** Test Case ***
Execute 2
        [Documentation]                 Expected connection break due to reboot
        Set Default Target Property     connection break is error       false
        ${result}                       Execute Command In Target       date;uname -a;uptime;shutdown -r now;while true;do echo waiting...;sleep 1;done     default
        Log                             ${result}
        Should Be Equal                 ${result.connection_ok}         True
        Should Be Equal                 ${result.close_ok}              False
        Set Default Target Property     connection break is error       true
        ${result}                       Execute Command In Target       date;uname -a;uptime
        Log                             ${result}
        Should Be Equal                 ${result.connection_ok} True
        Should Be Equal                 ${result.close_ok}      True

