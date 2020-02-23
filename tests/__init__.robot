*** Settings ***
Documentation       Initial Setup
Library            ../lib/redfish_client.py
Resource           ../testbeds.robot
Suite Setup        Run Keyword    RESTClient Init    ${REDFISH_SERVER_IP}    ${REDFISH_SERVER_PORT}    ${REDFISH_USERNAME}    ${REDFISH_PASSWORD}      				   
Suite Teardown     Run Keyword    RESTClient Close