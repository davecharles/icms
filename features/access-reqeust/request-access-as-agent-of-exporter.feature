Feature: Request Importer/Exporter Access as an Agent for an Exporter

    @access-request
    Scenario: Correct fields should be visible when user requests access as an agent of an importer
        When "som_user" logs in
        And  navigates to "access:request"
        And  sets Access Request Type to "Request access to act as an Agent for an Exporter"
        Then following fields are visible on access request form
            | Field                                                       | Visible |
            | Access Request Type                                         | True    |
            | Organisation name                                           | True    |
            | Organisation address                                        | True    |
            | What are you importing and where are you importing it from? | False   |
            | Agent name                                                  | True    |
            | Agent address                                               | True    |

    @access-request
    Scenario: User should see success message when request to act as an agent of an importer
        Given "some_user" is logged in
        When  the user requests to act as an agent of an exporter
        Then  a success message is displayed

    @access-request
    Scenario: User should see pending access requets
        Given "some_user" is logged in
        When  the user requests to act as an agent of an exporter 
        And navigates to "access:request"
        Then there are 1 pending access requests to act as an exporter