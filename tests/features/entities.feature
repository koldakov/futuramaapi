Feature: Request entity
  As a user,
  I want to add or delete some items from my shopping cart,
  So I can place order for my items.

  Scenario Outline: Get entity
  When The user requests the <entity_name> with id 1
  Then The FuturamaAPI server responds with the <entity_name>

  Examples:
  | entity_name |
  | character   |
  | episode     |
  | season      |
