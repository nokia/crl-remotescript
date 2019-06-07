# Copyright (C) 2019, Nokia

*** Settings ***

Library    Process
Library    OperatingSystem
Library    Collections
Library    crl.remotescript.RemoteScript    WITH NAME    RemoteScript

Test Setup    Remote Test Setup
Suite Teardown  Run Process  rm -rf /tmp/pdrobot-remotescript  shell=${True}

*** Variables ***
${TARGET_FILE}=  foo.sh
${TESTFILESIZE}=    1000000
${DEFAULT_TMPDIR}=  /tmp/default
&{DEFAULT_TARGET}=        cleanup=${True}
...                       connection break is error=${True}
...                       connection failure is error=${True}
...                       login prompt=login:${SPACE}
...                       login timeout=${60}
...                       max connection attempts=${10}
...                       nonzero status is error=${False}
...                       password prompt=Password:${SPACE}
...                       port=${None}
...                       prompt=\$${SPACE}
...                       su password=${None}
...                       su username=${None}
...                       use sudo user=${False}
*** Keywords ***
Remote Test Setup
    Set Default Target
    Set Sudo Target

Set Sudo Target
    [Arguments]  ${host}=${HOST1.host}  ${username}=${HOST1.user}  ${password}=${HOST1.password}
    RemoteScript.Set Target    host=${host}
    ...                        username=${username}
    ...                        password=${password}
    ...                        name=sudo
    RemoteScript.Set Target Property    sudo    su password    ${password}
    RemoteScript.Set Target Property    sudo    su username    root
    RemoteScript.Set Target Property    sudo    use sudo user    ${TRUE}

Set Default Target
    [Arguments]     ${host}=${HOST1.host}
    ...             ${username}=${HOST1.user}
    ...             ${password}=${HOST1.password}
    ...             ${target}=default
    RemoteScript.Set Target     host=${host}
    ...                         username=${username}
    ...                         password=${password}
    ...                         name=${target}

Create File In Target
    [Arguments]  ${target}=default  ${dir}=/tmp/${target}  ${file}=${TARGET_FILE}
    ${ret2}=    Execute Command In Target   touch ${dir}/${file}
    Should Be Equal As Integers     ${ret2.status}  0   ${ret2}

Workaround Create Directory In Target
    [Arguments]  ${target}=default  ${dir}=/tmp/${target}
    # TODO: issue [#10]
    # https://github.com/nokia/crl-remotescript/issues/10
    ${ret1}=    Execute Command In Target   mkdir -p ${dir}  target=${target}
    Should Be Equal As Integers     ${ret1.status}   0   ${ret1}

RemoteScript Create Directory In Target
    [Arguments]  ${target}=default
    Workaround Create Directory In Target  target=${target}
    # RemoteScript.Create Directory In Target  target=default  dir=${DEFAULT_TMPDIR}
    ${ret2}=    Execute Command In Target   stat ${DEFAULT_TMPDIR}
    Should Be Equal As Integers     ${ret2.status}  0   ${ret2}

RemoteScript Set Target With Sshkeyfile
    [Arguments]  ${target}=host2  ${host}=${HOST2}
    Set Target With Sshkeyfile  host=${host.host}
    ...                         username=${host.user}
    ...                         sshkeyfile=${host.key}
    ...                         name=${target}
    ${ret}=     Execute Command In Target   echo out    target=${target}
    Should Be Equal As Integers     ${ret.status}   0   ${ret}

RemoteScript Execute Command In Target
    [Arguments]     ${target}
    ${result}=     RemoteScript.Execute Command In Target
    ...            command=echo foo; echo bar>&2
    ...            target=${target}
    ...            timeout=10
    # Should Be Equal As Integers     ${result.status}    0   ${result}
    # Should Be Equal     ${result.stdout}    foo     ${result}
    # Should Be Equal     ${result.stderr}    bar     ${result}
    # Should Be Equal     ${result.status}   0
    # See issue 13 https://github.com/nokia/crl-remotescript/issues/13
    Run Keyword If  '${target}'=='sudo'
    ...             Should Be Equal     ${result.stdout}     foo\r\nbar
    Run Keyword If  '${target}'=='default'
    ...             Should Be Equal     ${result.stdout}    foo
    Run Keyword If  '${target}'=='default'
    ...             Should Be Equal     ${result.stderr}    bar
    Should Be Equal     ${result.connection_ok}     True

RemoteScript Execute Background Command In Target
    [Arguments]  ${target}
    FOR     ${exec_id}    IN    bg1  bg2  bg3
            Execute Background Command In Target    command=echo Hello;echo World!>&2
            ...                                     target=${target}  exec_id=${exec_id}
    END
    FOR     ${exec_id}    IN    bg1  bg2  bg3
            ${result}=    Wait Background Execution    ${exec_id}
            # Should Be Equal As Integers        ${result.status}    0   ${result}
            # Should Be Equal  ${result.stdout}    Hello   ${result}
            # Should Be Equal  ${result.stderr}    World!  ${result}
            # See issue 13 https://github.com/nokia/crl-remotescript/issues/13
            Run Keyword If  '${target}'=='sudo'
            ...             Should Be Equal     ${result.stdout}     Hello\r\nWorld!
            Run Keyword If  '${target}'=='default'
            ...             Should Be Equal     ${result.stdout}    Hello
            Run Keyword If  '${target}'=='default'
            ...             Should Be Equal     ${result.stderr}    World!
            Should Be Equal     ${result.connection_ok}     True
    END

RemoteScript Remove File Path Locally
    [Arguments]     ${filepath}
    Run Process     rm -rf ${filepath}  shell=${True}

RemoteScript Remove File Path In Target
    [Arguments]      ${target}   ${filepath}
    Execute Command In Target   command=rm -f ${filepath}  target=${target}

RemoteScript Remove File Path Locally And In Target
    [Arguments]     ${target}   ${remote_filepath}  ${local_filepath}
    RemoteScript Remove File Path Locally   filepath=${local_filepath}
    RemoteScript Remove File Path In Target     target=${target}
    ...                                         filepath=${remote_filepath}

RemoteScript Remove File Path In Two Remotes
    [Arguments]  ${target1}  ${target2}  ${filepath1}  ${filepath2}
    RemoteScript Remove File Path In Target     target=${target1}
    ...                                         filepath=${filepath1}
    RemoteScript Remove File Path In Target     target=${target2}
    ...                                         filepath=${filepath2}
*** Test Cases ***

Test Whoami
    ${ret}=     Execute Command In Target   command=whoami;whoami>&2
    Should Be Equal     ${ret.stdout}   host1   ${ret}
    Should Be Equal     ${ret.stderr}   host1   ${ret}
    # ${retsudo}=     Execute Command In Target   command=whoami;whoami>&2  target=sudo
    # Should Be Equal      ${retsudo.stdout}   root    ${retsudo}
    # Should Be Equal     ${retsudo.stderr}   root    ${retsudo}
    # See issue #13 https://github.com/nokia/crl-remotescript/issues/13

Test Echo With Su
    Set Sudo Target
    ${ret}=    RemoteScript.Execute Command In Target    echo out  timeout=5
    Should Be Equal    ${ret.status}   0
    Should Be Equal    ${ret.stdout}   out

Test Copy Directory To Target
    [Tags]  skip      #TODO: See issue [#10]
    Run Process     mkdir -p scripts  shell=${True}
    ${cpresult}=      RemoteScript.Copy Directory To Target
    ...     scripts
    ...     /tmp/my-robot-tc/scripts/
    Should Be Equal As Integers     ${cpresult.status}   0   ${cpresult}
    ${ret}=  Execute Command In Target   tar -cvzf target.tgz /tmp/my-robot-tc/scripts/
    Should Be Equal As Integers     ${ret.status}   0   ${ret}
    [Teardown]  RemoteScript Remove File Path Locally And In Target  target=default
    ...         remote_filepath=/tmp/my-robot-tc/scripts target.tgz
    ...         local_filepath=scripts

Templated RemoteScript Execute Command In Target
    [Template]  RemoteScript Execute Command In Target
    default
    sudo

Test RemoteScript Create Directory In Target Should Work
    RemoteScript Create Directory In Target
    ${ret2}=    Execute Command In Target   stat ${DEFAULT_TMPDIR}
    Should Be Equal As Integers     ${ret2.status}  0   ${ret2}
    [Teardown]  RemoteScript Remove File Path In Target
    ...         target=default
    ...         filepath=${DEFAULT_TMPDIR}

Templated Execute Background Command In Target
    [Template]  RemoteScript Execute Background Command In Target
    default
    sudo

Test RemoteScript Copy File To Target
    Run Process     touch  ./foo.sh
    RemoteScript Create Directory In Target
    ${ret2}=    Copy File To Target  source_file=./foo.sh  destination_dir=${DEFAULT_TMPDIR}
    Should Be Equal As Integers     ${ret2.status}   0   ${ret2}
    ${ret3}=    Execute Command In Target   stat ${DEFAULT_TMPDIR}/foo.sh
    Should Be Equal As Integers     ${ret3.status}  0   ${ret3}
    [Teardown]  RemoteScript Remove File Path Locally And In Target
    ...         target=default
    ...         remote_filepath=${DEFAULT_TMPDIR}
    ...         local_filepath=./foo.sh

Test Copy File From Target
    RemoteScript Create Directory In Target
    Create File In Target
    ${ret3}=    Copy File From Target   source_file=${DEFAULT_TMPDIR}/foo.sh  destination=.
    Should Be Equal As Integers     ${ret3.status}  0   ${ret3}
    File Should Exist   path=foo.sh
    [Teardown]  RemoteScript Remove File Path Locally And In Target
    ...         target=default
    ...         remote_filepath=${DEFAULT_TMPDIR}
    ...         local_filepath=./foo.sh

Test RemoteScript Remove Directory In Target
    RemoteScript Create Directory In Target
    ${ret2}=    Remove Directory In Target  path=${DEFAULT_TMPDIR}
    Should Be Equal As Integers     ${ret2.status}  0   ${ret2}
    ${ret3}=    Execute Command In Target   stat ${DEFAULT_TMPDIR}
    Should Be Equal As Integers     ${ret3.status}  1   ${ret3}

Test RemoteScript Set Target With Sshkeyfile
    RemoteScript Set Target With Sshkeyfile

Test RemoteScript Get Target Properties
    ${ret}=    Get Target Properties  target=default
    Dictionary Should Contain Sub Dictionary     ${ret}   ${DEFAULT_TARGET}

Test RemoteScript Execute Script In Target
    RemoteScript Create Directory In Target
    ${ret2}=    Copy File To Target  source_file=${CURDIR}/target_script.sh  destination_dir=${DEFAULT_TMPDIR}
    Should Be Equal As Integers     ${ret2.status}  0
    ${ret3}=     Execute Script In Target    file=${DEFAULT_TMPDIR}/target_script.sh
    Should Be Equal As Integers     ${ret3.status}  0
    [Teardown]  Execute Command In Target  rm -r ${DEFAULT_TMPDIR}

Test RemoteScript Execute Background Script In Target
    RemoteScript Create Directory In Target
    ${out}=     Run Process  ls ${CURDIR}  shell=${True}
    Log  ${out.stdout}
    ${ret2}=    Copy File To Target  source_file=${CURDIR}/target_script.sh  destination_dir=${DEFAULT_TMPDIR}
    Should Be Equal As Integers     ${ret2.status}  0
    Execute Background Script In Target  file=${DEFAULT_TMPDIR}/target_script.sh  target=default  exec_id=bg1
    ${result_bg1}=  Wait Background Execution   exec_id=bg1
    Log  ${result_bg1}
    Should Be Equal As Integers     ${result_bg1.status}   0
    [Teardown]  Execute Command In Target   rm -r ${DEFAULT_TMPDIR}

Test RemoteScript Copy File Between Targets
    RemoteScript Set Target With Sshkeyfile
    RemoteScript Create Directory In Target
    RemoteScript Create Directory In Target  target=host2
    Create File In Target
    ${ret}=     Copy File Between Targets
    ...         from_target=default
    ...         source_file=${DEFAULT_TMPDIR}/${TARGET_FILE}
    ...         to_target=host2
    ...         destination_dir=/tmp/host2
    Should Be Equal As Integers     ${ret.status}   0   ${ret}
    [Teardown]  RemoteScript Remove File Path In Two Remotes
    ...         target1=default
    ...         filepath1=${DEFAULT_TMPDIR}
    ...         target2=host2
    ...         filepath2=/tmp/host2${TARGET_FILE}

Test RemoteScript Kill Background Execution
    [Tags]  skip    #TODO: See issue [#11]
                    # https://github.com/nokia/crl-remotescript/issues/11
    Execute Background Command In Target    command=echo Hello; sleep 3   target=default  exec_id=bg1
    Sleep  1
    Kill Background Execution  exec_id=bg1
    ${ret}=     Wait Background Execution  exec_id=bg1
    Log  ${ret}

Test RemoteScript Set Target Property
    ${prop}=    Get Target Properties  target=default
    FOR     ${key}  IN  @{prop.keys()}
        Set Target Property  target_name=default  property_name=${key}  property_value=NewValue
        ${dict}=    Get Target Properties   target=default
        Should Be Equal     ${dict["${key}"]}   NewValue
    END
    FOR     ${key}  IN  @{prop.keys()}
        Set Target Property  target_name=default  property_name=${key}   property_value=${prop["${key}"]}
    END
    ${tprop}=   Get Target Properties  target=default
    Dictionary Should Contain Sub Dictionary  ${prop}  ${tprop}

Test RemoteScript Set Default Target Property
    RemoteScript Set Target With Sshkeyfile  target=host2
    ${tmp1}=    Get Target Properties   target=host2
    ${prop}=    Get Target Properties   target=default
    FOR     ${key}  IN  @{prop.keys()}
        Set Default Target Property  property_name=${key}    property_value=${prop["${key}"]}
    END
    ${tprop}=   Get Target Properties  target=host2
    Dictionary Should Contain Sub Dictionary  ${prop}   ${tprop}
