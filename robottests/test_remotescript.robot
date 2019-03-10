# Copyright (C) 2019, Nokia

*** Settings ***

Library    crl.remotescript.RemoteScript    WITH NAME    RemoteScript

Test Setup    Set RemoteScript Sudo Target
Force Tags     bug-crl-97

*** Variables ***

&{HOST}=    host=10.21.14.140
...         user=wrsroot
...         password=FinAdmin


*** Keywords ***
Set RemoteScript Sudo Target
    RemoteScript.Set Target    host=${HOST.host}
    ...                        username=${HOST.user}
    ...                        password=${HOST.password}
    RemoteScript.Set Target Property    default    su password    ${HOST.password}
    RemoteScript.Set Target Property    default    su username    root
    RemoteScript.Set Target Property    default    use sudo user    ${TRUE}


*** Test Cases ***

Test Echo With Su
    ${ret}=    RemoteScript.Execute Command In Target    echo out
    Should Be Equal    ${ret.status}   0
    Should Be Equal    ${ret.stdout}   out
