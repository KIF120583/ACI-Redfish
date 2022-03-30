*** Settings ***
Library            ../lib/redfish_client.py
Resource           ../testbeds.robot
Suite Setup        Run Keyword    RESTClient Init    ${REDFISH_SERVER_IP}    ${REDFISH_SERVER_PORT}    ${REDFISH_USERNAME}    ${REDFISH_PASSWORD}      				   
Suite Teardown     Run Keyword    RESTClient Close
*** Test Cases ***
Get example
    RESTClient Get    /redfish/v1/
    ${status}    RESTClient Get response status
    Should be equal    ${status}    ${200}
    
Post example
    RESTClient Post    /redfish/v1/Managers/bmc/LogServices/SEL/Actions/LogService.ClearLog    {}
    ${status}    RESTClient Get response status
    Should be equal    ${status}    ${204}
    
Patch example
    REST PATCH    /redfish/v1/SessionService    {"SessionTimeout":500}
    ${res_body}    RESTClient Get response body
    Should be equal    ${res_body}[SessionTimeout]    ${500}
    REST PATCH    /redfish/v1/SessionService    {"SessionTimeout":300}
    ${res_body}    RESTClient Get response body
    Should be equal    ${res_body}[SessionTimeout]    ${300}
    
*** Keywords ***
REST PATCH
    [Arguments]    ${url}    ${body}
    RESTClient Get    ${url}
    ${status}    RESTClient Get response status
    Should be equal    ${status}    ${200}
    
    RESTClient Patch    ${url}    ${body}
    ${status}    RESTClient Get response status
    Should be equal    ${status}    ${200}