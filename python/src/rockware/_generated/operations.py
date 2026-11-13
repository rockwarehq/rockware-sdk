# Made by scripts/generate.py from the repo's schema/, operations/ and behavior.json. Don't edit it.
"""One method per operation in operations/. The clients fill in how they're sent."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from datetime import datetime
from typing import Any

from .._operation import DEFAULT_MAX_PAGES, Operation
from .types import *  # noqa: F403

OPERATIONS: dict[str, Operation] = {
    "GetSite": Operation(
        name="GetSite",
        root="site",
        mutation=False,
        safe_to_repeat=True,
        document="query GetSite {\n  site {\n    ...SiteFields\n  }\n}\n\nfragment SiteFields on Site {\n  id\n  name\n  description\n  timezone\n  updatedAt\n}",
    ),
    "GetWorkcenter": Operation(
        name="GetWorkcenter",
        root="workcenter",
        mutation=False,
        safe_to_repeat=True,
        document="query GetWorkcenter($id: ID!) {\n  workcenter(id: $id) {\n    ...WorkcenterFields\n  }\n}\n\nfragment WorkcenterFields on Workcenter {\n  id\n  name\n  description\n  parentId\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListWorkcenters": Operation(
        name="ListWorkcenters",
        root="workcenters",
        mutation=False,
        safe_to_repeat=True,
        document="query ListWorkcenters($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  workcenters(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...WorkcenterFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment WorkcenterFields on Workcenter {\n  id\n  name\n  description\n  parentId\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "GetStation": Operation(
        name="GetStation",
        root="station",
        mutation=False,
        safe_to_repeat=True,
        document="query GetStation($id: ID!) {\n  station(id: $id) {\n    ...StationFields\n  }\n}\n\nfragment StationFields on Station {\n  id\n  name\n  description\n  sortOrder\n  workcenterId\n  workcenter {\n    id\n    name\n  }\n  currentJobId\n  currentJob {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListStations": Operation(
        name="ListStations",
        root="stations",
        mutation=False,
        safe_to_repeat=True,
        document="query ListStations($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  stations(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...StationFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment StationFields on Station {\n  id\n  name\n  description\n  sortOrder\n  workcenterId\n  workcenter {\n    id\n    name\n  }\n  currentJobId\n  currentJob {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "GetCustomer": Operation(
        name="GetCustomer",
        root="customer",
        mutation=False,
        safe_to_repeat=True,
        document="query GetCustomer($id: ID!) {\n  customer(id: $id) {\n    ...CustomerFields\n  }\n}\n\nfragment CustomerFields on Customer {\n  id\n  name\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListCustomers": Operation(
        name="ListCustomers",
        root="customers",
        mutation=False,
        safe_to_repeat=True,
        document="query ListCustomers($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  customers(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...CustomerFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment CustomerFields on Customer {\n  id\n  name\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "GetMaterial": Operation(
        name="GetMaterial",
        root="material",
        mutation=False,
        safe_to_repeat=True,
        document="query GetMaterial($id: ID!) {\n  material(id: $id) {\n    ...MaterialFields\n  }\n}\n\nfragment MaterialFields on Material {\n  id\n  materialNumber\n  name\n  description\n  classification\n  shortCode\n  externalNumber\n  unitCost\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListMaterials": Operation(
        name="ListMaterials",
        root="materials",
        mutation=False,
        safe_to_repeat=True,
        document="query ListMaterials($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  materials(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...MaterialFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment MaterialFields on Material {\n  id\n  materialNumber\n  name\n  description\n  classification\n  shortCode\n  externalNumber\n  unitCost\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "GetProduct": Operation(
        name="GetProduct",
        root="product",
        mutation=False,
        safe_to_repeat=True,
        document="query GetProduct($id: ID!) {\n  product(id: $id) {\n    ...ProductFields\n  }\n}\n\nfragment ProductFields on Product {\n  id\n  sku\n  name\n  description\n  externalSku\n  itemCost\n  weight\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListProducts": Operation(
        name="ListProducts",
        root="products",
        mutation=False,
        safe_to_repeat=True,
        document="query ListProducts($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  products(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...ProductFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment ProductFields on Product {\n  id\n  sku\n  name\n  description\n  externalSku\n  itemCost\n  weight\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "GetTool": Operation(
        name="GetTool",
        root="tool",
        mutation=False,
        safe_to_repeat=True,
        document="query GetTool($id: ID!) {\n  tool(id: $id) {\n    ...ToolFields\n  }\n}\n\nfragment ToolFields on Tool {\n  id\n  name\n  description\n  cavityCount\n  cavities {\n    id\n    name\n    position\n  }\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListTools": Operation(
        name="ListTools",
        root="tools",
        mutation=False,
        safe_to_repeat=True,
        document="query ListTools($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  tools(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...ToolFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment ToolFields on Tool {\n  id\n  name\n  description\n  cavityCount\n  cavities {\n    id\n    name\n    position\n  }\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "GetJob": Operation(
        name="GetJob",
        root="job",
        mutation=False,
        safe_to_repeat=True,
        document="query GetJob($id: ID!) {\n  job(id: $id) {\n    ...JobFields\n  }\n}\n\nfragment JobFields on Job {\n  id\n  name\n  description\n  version\n  standardRate\n  standardRateUnit\n  standardRatePeriod\n  standardCycle\n  standardQuantity\n  productsPerCycle\n  profileId\n  tools {\n    id\n    name\n  }\n  items {\n    id\n    quantity\n    isActive\n    cavityId\n    product {\n      id\n      sku\n    }\n    tool {\n      id\n      name\n    }\n  }\n  eligibleStations {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListJobs": Operation(
        name="ListJobs",
        root="jobs",
        mutation=False,
        safe_to_repeat=True,
        document="query ListJobs($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  jobs(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...JobFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment JobFields on Job {\n  id\n  name\n  description\n  version\n  standardRate\n  standardRateUnit\n  standardRatePeriod\n  standardCycle\n  standardQuantity\n  productsPerCycle\n  profileId\n  tools {\n    id\n    name\n  }\n  items {\n    id\n    quantity\n    isActive\n    cavityId\n    product {\n      id\n      sku\n    }\n    tool {\n      id\n      name\n    }\n  }\n  eligibleStations {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "GetOrder": Operation(
        name="GetOrder",
        root="order",
        mutation=False,
        safe_to_repeat=True,
        document="query GetOrder($id: ID!) {\n  order(id: $id) {\n    ...OrderFields\n  }\n}\n\nfragment OrderFields on Order {\n  id\n  orderNumber\n  poNumber\n  status\n  notes\n  customerId\n  customer {\n    id\n    name\n  }\n  defaultTargetQuantity\n  startDate\n  dueDate\n  openedAt\n  completedAt\n  cancelledAt\n  lines {\n    id\n    productId\n    product {\n      id\n      sku\n    }\n    targetQuantity\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListOrders": Operation(
        name="ListOrders",
        root="orders",
        mutation=False,
        safe_to_repeat=True,
        document="query ListOrders($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  orders(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...OrderFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment OrderFields on Order {\n  id\n  orderNumber\n  poNumber\n  status\n  notes\n  customerId\n  customer {\n    id\n    name\n  }\n  defaultTargetQuantity\n  startDate\n  dueDate\n  openedAt\n  completedAt\n  cancelledAt\n  lines {\n    id\n    productId\n    product {\n      id\n      sku\n    }\n    targetQuantity\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "GetProductionRun": Operation(
        name="GetProductionRun",
        root="productionRun",
        mutation=False,
        safe_to_repeat=True,
        document="query GetProductionRun($id: ID!) {\n  productionRun(id: $id) {\n    ...ProductionRunFields\n  }\n}\n\nfragment ProductionRunFields on ProductionRun {\n  id\n  status\n  rank\n  stationId\n  station {\n    id\n    name\n  }\n  workcenterId\n  jobId\n  job {\n    id\n    name\n  }\n  parts {\n    productId\n    product {\n      id\n      sku\n    }\n    perCycle\n    requiredGood\n    goodCount\n    scrapCount\n    metAt\n  }\n  startBy\n  endBy\n  startByMissed\n  endByMissed\n  plannedStart\n  plannedEnd\n  plannedBusinessDate\n  plannedShiftName\n  plannedChangeoverMinutes\n  actualChangeoverMinutes\n  runStartedAt\n  quantityMetAt\n  closedAt\n  closedBusinessDate\n  closeReason\n  skipCount\n  jobChangedAt\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListProductionRuns": Operation(
        name="ListProductionRuns",
        root="productionRuns",
        mutation=False,
        safe_to_repeat=True,
        document="query ListProductionRuns($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  productionRuns(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...ProductionRunFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment ProductionRunFields on ProductionRun {\n  id\n  status\n  rank\n  stationId\n  station {\n    id\n    name\n  }\n  workcenterId\n  jobId\n  job {\n    id\n    name\n  }\n  parts {\n    productId\n    product {\n      id\n      sku\n    }\n    perCycle\n    requiredGood\n    goodCount\n    scrapCount\n    metAt\n  }\n  startBy\n  endBy\n  startByMissed\n  endByMissed\n  plannedStart\n  plannedEnd\n  plannedBusinessDate\n  plannedShiftName\n  plannedChangeoverMinutes\n  actualChangeoverMinutes\n  runStartedAt\n  quantityMetAt\n  closedAt\n  closedBusinessDate\n  closeReason\n  skipCount\n  jobChangedAt\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "GetStationLineup": Operation(
        name="GetStationLineup",
        root="station",
        mutation=False,
        safe_to_repeat=True,
        document="query GetStationLineup($id: ID!) {\n  station(id: $id) {\n    id\n    name\n    lineup {\n      position\n      predictedChangeoverStart\n      predictedStart\n      predictedEnd\n      startByAtRisk\n      endByAtRisk\n      progress {\n        productId\n        requiredGood\n        good\n        scrap\n      }\n      run {\n        ...ProductionRunFields\n      }\n    }\n  }\n}\n\nfragment ProductionRunFields on ProductionRun {\n  id\n  status\n  rank\n  stationId\n  station {\n    id\n    name\n  }\n  workcenterId\n  jobId\n  job {\n    id\n    name\n  }\n  parts {\n    productId\n    product {\n      id\n      sku\n    }\n    perCycle\n    requiredGood\n    goodCount\n    scrapCount\n    metAt\n  }\n  startBy\n  endBy\n  startByMissed\n  endByMissed\n  plannedStart\n  plannedEnd\n  plannedBusinessDate\n  plannedShiftName\n  plannedChangeoverMinutes\n  actualChangeoverMinutes\n  runStartedAt\n  quantityMetAt\n  closedAt\n  closedBusinessDate\n  closeReason\n  skipCount\n  jobChangedAt\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListEntityModels": Operation(
        name="ListEntityModels",
        root="entityModels",
        mutation=False,
        safe_to_repeat=True,
        document="query ListEntityModels {\n  entityModels {\n    ...EntityModelFields\n  }\n}\n\nfragment EntityModelFields on EntityModel {\n  id\n  key\n  label\n  description\n  version\n  fields {\n    key\n    label\n    description\n    type\n    required\n    isList\n    refModel\n    options {\n      value\n      label\n    }\n  }\n  createdAt\n  updatedAt\n}",
    ),
    "GetEntityModel": Operation(
        name="GetEntityModel",
        root="entityModel",
        mutation=False,
        safe_to_repeat=True,
        document="query GetEntityModel($key: String!) {\n  entityModel(key: $key) {\n    ...EntityModelFields\n  }\n}\n\nfragment EntityModelFields on EntityModel {\n  id\n  key\n  label\n  description\n  version\n  fields {\n    key\n    label\n    description\n    type\n    required\n    isList\n    refModel\n    options {\n      value\n      label\n    }\n  }\n  createdAt\n  updatedAt\n}",
    ),
    "GetEntityRecord": Operation(
        name="GetEntityRecord",
        root="entityRecord",
        mutation=False,
        safe_to_repeat=True,
        document="query GetEntityRecord($id: ID!) {\n  entityRecord(id: $id) {\n    ...EntityRecordFields\n  }\n}\n\nfragment EntityRecordFields on EntityRecord {\n  id\n  model\n  name\n  values\n  deleted\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListEntityRecords": Operation(
        name="ListEntityRecords",
        root="entityRecords",
        mutation=False,
        safe_to_repeat=True,
        document="query ListEntityRecords($model: String!, $first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  entityRecords(\n    model: $model\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...EntityRecordFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment EntityRecordFields on EntityRecord {\n  id\n  model\n  name\n  values\n  deleted\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
    ),
    "ListWebhooks": Operation(
        name="ListWebhooks",
        root="webhooks",
        mutation=False,
        safe_to_repeat=True,
        document="query ListWebhooks {\n  webhooks {\n    ...WebhookFields\n  }\n}\n\nfragment WebhookFields on Webhook {\n  id\n  url\n  events\n  enabled\n  createdAt\n  updatedAt\n}",
    ),
    "ListWebhookDeliveries": Operation(
        name="ListWebhookDeliveries",
        root="webhookDeliveries",
        mutation=False,
        safe_to_repeat=True,
        document="query ListWebhookDeliveries($webhookId: ID!, $status: WebhookDeliveryStatus, $first: Int) {\n  webhookDeliveries(webhookId: $webhookId, status: $status, first: $first) {\n    ...WebhookDeliveryFields\n  }\n}\n\nfragment WebhookDeliveryFields on WebhookDelivery {\n  id\n  eventId\n  type\n  status\n  attempts\n  responseStatus\n  error\n  startedAt\n  finishedAt\n  nextAttemptAt\n}",
    ),
    "CreateWebhook": Operation(
        name="CreateWebhook",
        root="createWebhook",
        mutation=True,
        safe_to_repeat=False,
        document="mutation CreateWebhook($webhook: WebhookInput!) {\n  createWebhook(webhook: $webhook) {\n    secret\n    webhook {\n      ...WebhookFields\n    }\n  }\n}\n\nfragment WebhookFields on Webhook {\n  id\n  url\n  events\n  enabled\n  createdAt\n  updatedAt\n}",
    ),
    "UpdateWebhook": Operation(
        name="UpdateWebhook",
        root="updateWebhook",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpdateWebhook($id: ID!, $webhook: WebhookUpdateInput!) {\n  updateWebhook(id: $id, webhook: $webhook) {\n    ...WebhookFields\n  }\n}\n\nfragment WebhookFields on Webhook {\n  id\n  url\n  events\n  enabled\n  createdAt\n  updatedAt\n}",
    ),
    "DeleteWebhook": Operation(
        name="DeleteWebhook",
        root="deleteWebhook",
        mutation=True,
        safe_to_repeat=False,
        document="mutation DeleteWebhook($id: ID!) {\n  deleteWebhook(id: $id)\n}",
    ),
    "RotateWebhookSecret": Operation(
        name="RotateWebhookSecret",
        root="rotateWebhookSecret",
        mutation=True,
        safe_to_repeat=False,
        document="mutation RotateWebhookSecret($id: ID!) {\n  rotateWebhookSecret(id: $id) {\n    secret\n    webhook {\n      ...WebhookFields\n    }\n  }\n}\n\nfragment WebhookFields on Webhook {\n  id\n  url\n  events\n  enabled\n  createdAt\n  updatedAt\n}",
    ),
    "SendTestWebhook": Operation(
        name="SendTestWebhook",
        root="sendTestWebhook",
        mutation=True,
        safe_to_repeat=False,
        document="mutation SendTestWebhook($id: ID!) {\n  sendTestWebhook(id: $id) {\n    ...WebhookDeliveryFields\n  }\n}\n\nfragment WebhookDeliveryFields on WebhookDelivery {\n  id\n  eventId\n  type\n  status\n  attempts\n  responseStatus\n  error\n  startedAt\n  finishedAt\n  nextAttemptAt\n}",
    ),
    "RedeliverWebhook": Operation(
        name="RedeliverWebhook",
        root="redeliverWebhook",
        mutation=True,
        safe_to_repeat=False,
        document="mutation RedeliverWebhook($deliveryId: ID!) {\n  redeliverWebhook(deliveryId: $deliveryId) {\n    ...WebhookDeliveryFields\n  }\n}\n\nfragment WebhookDeliveryFields on WebhookDelivery {\n  id\n  eventId\n  type\n  status\n  attempts\n  responseStatus\n  error\n  startedAt\n  finishedAt\n  nextAttemptAt\n}",
    ),
    "UpsertWorkcenters": Operation(
        name="UpsertWorkcenters",
        root="upsertWorkcenters",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpsertWorkcenters($workcenters: [WorkcenterInput!]!, $source: String) {\n  upsertWorkcenters(workcenters: $workcenters, source: $source) {\n    results {\n      externalId\n      action\n      workcenter {\n        ...WorkcenterFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment WorkcenterFields on Workcenter {\n  id\n  name\n  description\n  parentId\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "UpsertStations": Operation(
        name="UpsertStations",
        root="upsertStations",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpsertStations($stations: [StationInput!]!, $source: String) {\n  upsertStations(stations: $stations, source: $source) {\n    results {\n      externalId\n      action\n      station {\n        ...StationFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment StationFields on Station {\n  id\n  name\n  description\n  sortOrder\n  workcenterId\n  workcenter {\n    id\n    name\n  }\n  currentJobId\n  currentJob {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "UpsertCustomers": Operation(
        name="UpsertCustomers",
        root="upsertCustomers",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpsertCustomers($customers: [CustomerUpsertInput!]!, $source: String) {\n  upsertCustomers(customers: $customers, source: $source) {\n    results {\n      externalId\n      action\n      customer {\n        ...CustomerFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment CustomerFields on Customer {\n  id\n  name\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "UpsertMaterials": Operation(
        name="UpsertMaterials",
        root="upsertMaterials",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpsertMaterials($materials: [MaterialInput!]!, $source: String) {\n  upsertMaterials(materials: $materials, source: $source) {\n    results {\n      externalId\n      action\n      material {\n        ...MaterialFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment MaterialFields on Material {\n  id\n  materialNumber\n  name\n  description\n  classification\n  shortCode\n  externalNumber\n  unitCost\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "UpsertProducts": Operation(
        name="UpsertProducts",
        root="upsertProducts",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpsertProducts($products: [ProductInput!]!, $source: String) {\n  upsertProducts(products: $products, source: $source) {\n    results {\n      externalId\n      action\n      product {\n        ...ProductFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment ProductFields on Product {\n  id\n  sku\n  name\n  description\n  externalSku\n  itemCost\n  weight\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "UpsertTools": Operation(
        name="UpsertTools",
        root="upsertTools",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpsertTools($tools: [ToolInput!]!, $source: String) {\n  upsertTools(tools: $tools, source: $source) {\n    results {\n      externalId\n      action\n      tool {\n        ...ToolFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment ToolFields on Tool {\n  id\n  name\n  description\n  cavityCount\n  cavities {\n    id\n    name\n    position\n  }\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "UpsertJobs": Operation(
        name="UpsertJobs",
        root="upsertJobs",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpsertJobs($jobs: [JobInput!]!, $source: String) {\n  upsertJobs(jobs: $jobs, source: $source) {\n    results {\n      externalId\n      action\n      job {\n        ...JobFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment JobFields on Job {\n  id\n  name\n  description\n  version\n  standardRate\n  standardRateUnit\n  standardRatePeriod\n  standardCycle\n  standardQuantity\n  productsPerCycle\n  profileId\n  tools {\n    id\n    name\n  }\n  items {\n    id\n    quantity\n    isActive\n    cavityId\n    product {\n      id\n      sku\n    }\n    tool {\n      id\n      name\n    }\n  }\n  eligibleStations {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "UpsertProductionRuns": Operation(
        name="UpsertProductionRuns",
        root="upsertProductionRuns",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpsertProductionRuns($runs: [ProductionRunInput!]!, $source: String) {\n  upsertProductionRuns(runs: $runs, source: $source) {\n    results {\n      externalId\n      action\n      run {\n        ...ProductionRunFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment ProductionRunFields on ProductionRun {\n  id\n  status\n  rank\n  stationId\n  station {\n    id\n    name\n  }\n  workcenterId\n  jobId\n  job {\n    id\n    name\n  }\n  parts {\n    productId\n    product {\n      id\n      sku\n    }\n    perCycle\n    requiredGood\n    goodCount\n    scrapCount\n    metAt\n  }\n  startBy\n  endBy\n  startByMissed\n  endByMissed\n  plannedStart\n  plannedEnd\n  plannedBusinessDate\n  plannedShiftName\n  plannedChangeoverMinutes\n  actualChangeoverMinutes\n  runStartedAt\n  quantityMetAt\n  closedAt\n  closedBusinessDate\n  closeReason\n  skipCount\n  jobChangedAt\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "UpsertOrder": Operation(
        name="UpsertOrder",
        root="upsertOrder",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpsertOrder($order: OrderInput!, $source: String) {\n  upsertOrder(order: $order, source: $source) {\n    action\n    order {\n      ...OrderFields\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment OrderFields on Order {\n  id\n  orderNumber\n  poNumber\n  status\n  notes\n  customerId\n  customer {\n    id\n    name\n  }\n  defaultTargetQuantity\n  startDate\n  dueDate\n  openedAt\n  completedAt\n  cancelledAt\n  lines {\n    id\n    productId\n    product {\n      id\n      sku\n    }\n    targetQuantity\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "SequenceLineup": Operation(
        name="SequenceLineup",
        root="sequenceLineup",
        mutation=True,
        safe_to_repeat=True,
        document="mutation SequenceLineup($station: String!, $runs: [String!]!, $source: String) {\n  sequenceLineup(station: $station, runs: $runs, source: $source) {\n    action\n    station {\n      id\n      name\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "LinkExternalIds": Operation(
        name="LinkExternalIds",
        root="linkExternalIds",
        mutation=True,
        safe_to_repeat=True,
        document="mutation LinkExternalIds($kind: ExternalIdKind!, $links: [ExternalIdLinkInput!]!, $source: String) {\n  linkExternalIds(kind: $kind, links: $links, source: $source) {\n    results {\n      id\n      externalId\n      action\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "UpsertEntityModels": Operation(
        name="UpsertEntityModels",
        root="upsertEntityModels",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpsertEntityModels($models: [EntityModelInput!]!) {\n  upsertEntityModels(models: $models) {\n    results {\n      key\n      action\n      model {\n        ...EntityModelFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment EntityModelFields on EntityModel {\n  id\n  key\n  label\n  description\n  version\n  fields {\n    key\n    label\n    description\n    type\n    required\n    isList\n    refModel\n    options {\n      value\n      label\n    }\n  }\n  createdAt\n  updatedAt\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
    "UpsertEntityRecords": Operation(
        name="UpsertEntityRecords",
        root="upsertEntityRecords",
        mutation=True,
        safe_to_repeat=True,
        document="mutation UpsertEntityRecords($model: String!, $records: [EntityRecordInput!]!, $source: String) {\n  upsertEntityRecords(model: $model, records: $records, source: $source) {\n    results {\n      externalId\n      action\n      record {\n        ...EntityRecordFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment EntityRecordFields on EntityRecord {\n  id\n  model\n  name\n  values\n  deleted\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
    ),
}

PAGEABLE = 10


class SyncOperations(ABC):
    @abstractmethod
    def _run(self, operation: Operation, variables: dict[str, Any]) -> Any: ...

    @abstractmethod
    def _run_pages(self, operation: Operation, variables: dict[str, Any], max_pages: int) -> Iterator[Any]: ...

    def get_site(self) -> SiteFields | None:
        return self._run(OPERATIONS["GetSite"], {})

    def get_workcenter(self, *, id: str) -> WorkcenterFields | None:
        return self._run(OPERATIONS["GetWorkcenter"], {"id": id})

    def list_workcenters(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListWorkcentersResult:
        """Workcenter records at your site, oldest change first."""
        return self._run(
            OPERATIONS["ListWorkcenters"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_workcenters(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> Iterator[WorkcenterFields]:
        """Every record from list_workcenters, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListWorkcenters"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    def get_station(self, *, id: str) -> StationFields | None:
        return self._run(OPERATIONS["GetStation"], {"id": id})

    def list_stations(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListStationsResult:
        """Station records at your site, oldest change first."""
        return self._run(
            OPERATIONS["ListStations"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_stations(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> Iterator[StationFields]:
        """Every record from list_stations, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListStations"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    def get_customer(self, *, id: str) -> CustomerFields | None:
        return self._run(OPERATIONS["GetCustomer"], {"id": id})

    def list_customers(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListCustomersResult:
        """Customer records at your site, oldest change first."""
        return self._run(
            OPERATIONS["ListCustomers"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_customers(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> Iterator[CustomerFields]:
        """Every record from list_customers, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListCustomers"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    def get_material(self, *, id: str) -> MaterialFields | None:
        return self._run(OPERATIONS["GetMaterial"], {"id": id})

    def list_materials(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListMaterialsResult:
        """Material records at your site, oldest change first."""
        return self._run(
            OPERATIONS["ListMaterials"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_materials(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> Iterator[MaterialFields]:
        """Every record from list_materials, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListMaterials"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    def get_product(self, *, id: str) -> ProductFields | None:
        return self._run(OPERATIONS["GetProduct"], {"id": id})

    def list_products(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListProductsResult:
        """Product records at your site, oldest change first."""
        return self._run(
            OPERATIONS["ListProducts"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_products(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> Iterator[ProductFields]:
        """Every record from list_products, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListProducts"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    def get_tool(self, *, id: str) -> ToolFields | None:
        return self._run(OPERATIONS["GetTool"], {"id": id})

    def list_tools(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListToolsResult:
        """Tool records at your site, oldest change first."""
        return self._run(
            OPERATIONS["ListTools"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_tools(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> Iterator[ToolFields]:
        """Every record from list_tools, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListTools"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    def get_job(self, *, id: str) -> JobFields | None:
        return self._run(OPERATIONS["GetJob"], {"id": id})

    def list_jobs(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListJobsResult:
        """Job records at your site, oldest change first."""
        return self._run(
            OPERATIONS["ListJobs"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_jobs(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> Iterator[JobFields]:
        """Every record from list_jobs, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListJobs"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    def get_order(self, *, id: str) -> OrderFields | None:
        return self._run(OPERATIONS["GetOrder"], {"id": id})

    def list_orders(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListOrdersResult:
        """Order records at your site, oldest change first."""
        return self._run(
            OPERATIONS["ListOrders"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_orders(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> Iterator[OrderFields]:
        """Every record from list_orders, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListOrders"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    def get_production_run(self, *, id: str) -> ProductionRunFields | None:
        return self._run(OPERATIONS["GetProductionRun"], {"id": id})

    def list_production_runs(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListProductionRunsResult:
        """ProductionRun records at your site, oldest change first."""
        return self._run(
            OPERATIONS["ListProductionRuns"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_production_runs(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> Iterator[ProductionRunFields]:
        """Every record from list_production_runs, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListProductionRuns"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    def get_station_lineup(self, *, id: str) -> GetStationLineupResult | None:
        return self._run(OPERATIONS["GetStationLineup"], {"id": id})

    def list_entity_models(self) -> list[EntityModelFields]:
        """The custom entities at your site, with their fields."""
        return self._run(OPERATIONS["ListEntityModels"], {})

    def get_entity_model(self, *, key: str) -> EntityModelFields | None:
        return self._run(OPERATIONS["GetEntityModel"], {"key": key})

    def get_entity_record(self, *, id: str) -> EntityRecordFields | None:
        return self._run(OPERATIONS["GetEntityRecord"], {"id": id})

    def list_entity_records(
        self,
        *,
        model: str,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListEntityRecordsResult:
        """One custom entity's records, oldest change first."""
        return self._run(
            OPERATIONS["ListEntityRecords"],
            {
                "model": model,
                "first": first,
                "after": after,
                "updatedSince": updated_since,
                "includeDeleted": include_deleted,
            },
        )

    def list_all_entity_records(
        self,
        *,
        model: str,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> Iterator[EntityRecordFields]:
        """Every record from list_entity_records, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListEntityRecords"],
            {"model": model, "first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    def list_webhooks(self) -> list[WebhookFields]:
        """This site's webhooks. Needs webhooks:write."""
        return self._run(OPERATIONS["ListWebhooks"], {})

    def list_webhook_deliveries(
        self, *, webhook_id: str, status: WebhookDeliveryStatus | None = None, first: int | None = None
    ) -> list[WebhookDeliveryFields]:
        """A webhook's deliveries, newest first. Needs webhooks:write."""
        return self._run(
            OPERATIONS["ListWebhookDeliveries"], {"webhookId": webhook_id, "status": status, "first": first}
        )

    def create_webhook(self, *, webhook: WebhookInput) -> CreateWebhookResult:
        """Make a webhook. Its signing secret is in the answer, and only there. Needs webhooks:write."""
        return self._run(OPERATIONS["CreateWebhook"], {"webhook": webhook})

    def update_webhook(self, *, id: str, webhook: WebhookUpdateInput) -> WebhookFields:
        """Change a webhook's URL, events or whether it's on. Needs webhooks:write."""
        return self._run(OPERATIONS["UpdateWebhook"], {"id": id, "webhook": webhook})

    def delete_webhook(self, *, id: str) -> bool:
        """Delete a webhook. Its retries stop. Needs webhooks:write."""
        return self._run(OPERATIONS["DeleteWebhook"], {"id": id})

    def rotate_webhook_secret(self, *, id: str) -> RotateWebhookSecretResult:
        """Give a webhook a new signing secret. The old one stops working now. Needs webhooks:write."""
        return self._run(OPERATIONS["RotateWebhookSecret"], {"id": id})

    def send_test_webhook(self, *, id: str) -> WebhookDeliveryFields:
        """Send a "webhook.test" event now, and see how your URL answered. Needs webhooks:write."""
        return self._run(OPERATIONS["SendTestWebhook"], {"id": id})

    def redeliver_webhook(self, *, delivery_id: str) -> WebhookDeliveryFields:
        """Send a delivery again, soon. Needs webhooks:write."""
        return self._run(OPERATIONS["RedeliverWebhook"], {"deliveryId": delivery_id})

    def upsert_workcenters(
        self, *, workcenters: list[WorkcenterInput], source: str | None = None
    ) -> UpsertWorkcentersResult:
        """Send up to 100 workcenters. All or nothing."""
        return self._run(OPERATIONS["UpsertWorkcenters"], {"workcenters": workcenters, "source": source})

    def upsert_stations(self, *, stations: list[StationInput], source: str | None = None) -> UpsertStationsResult:
        """Send up to 100 stations. All or nothing. Send workcenters first."""
        return self._run(OPERATIONS["UpsertStations"], {"stations": stations, "source": source})

    def upsert_customers(
        self, *, customers: list[CustomerUpsertInput], source: str | None = None
    ) -> UpsertCustomersResult:
        """Send up to 100 customers. All or nothing."""
        return self._run(OPERATIONS["UpsertCustomers"], {"customers": customers, "source": source})

    def upsert_materials(self, *, materials: list[MaterialInput], source: str | None = None) -> UpsertMaterialsResult:
        """Send up to 100 materials. All or nothing: if one has a problem, none are saved."""
        return self._run(OPERATIONS["UpsertMaterials"], {"materials": materials, "source": source})

    def upsert_products(self, *, products: list[ProductInput], source: str | None = None) -> UpsertProductsResult:
        """Send up to 100 products, with their bills of materials. All or nothing: if one has a problem, none are saved. Send materials first."""
        return self._run(OPERATIONS["UpsertProducts"], {"products": products, "source": source})

    def upsert_tools(self, *, tools: list[ToolInput], source: str | None = None) -> UpsertToolsResult:
        """Send up to 100 tools, with their cavities. All or nothing."""
        return self._run(OPERATIONS["UpsertTools"], {"tools": tools, "source": source})

    def upsert_jobs(self, *, jobs: list[JobInput], source: str | None = None) -> UpsertJobsResult:
        """Send up to 100 jobs, with their tools and the products they make. All or nothing. Send tools and products first."""
        return self._run(OPERATIONS["UpsertJobs"], {"jobs": jobs, "source": source})

    def upsert_production_runs(
        self, *, runs: list[ProductionRunInput], source: str | None = None
    ) -> UpsertProductionRunsResult:
        """Send up to 100 runs to stations' lineups. A new run goes to the end of its station's queue; an update never moves it, because the plant can reorder runs. Changing a queued run's station or job takes it off and adds it again at the end. The lineup's rules are the same as in IMM: a running run can change its counts and dates only, and a closed one nothing. Safe to send again."""
        return self._run(OPERATIONS["UpsertProductionRuns"], {"runs": runs, "source": source})

    def upsert_order(self, *, order: OrderInput, source: str | None = None) -> UpsertOrderResult:
        """Send one order, with its customer and lines. Safe to send again: the same order gives the same result."""
        return self._run(OPERATIONS["UpsertOrder"], {"order": order, "source": source})

    def sequence_lineup(self, *, station: str, runs: list[str], source: str | None = None) -> SequenceLineupResult:
        """Put runs in order at one station, by your ids. They take the places they already hold in its queue, in the order given, and every other run stays where it is. Only queued runs. Safe to send again."""
        return self._run(OPERATIONS["SequenceLineup"], {"station": station, "runs": runs, "source": source})

    def link_external_ids(
        self, *, kind: ExternalIdKind, links: list[ExternalIdLinkInput], source: str | None = None
    ) -> LinkExternalIdsResult:
        """Give up to 100 records made in IMM your own ids, by their id in IMM. From then on you can use your id wherever the API takes theirs, and renaming them in IMM changes nothing. An id another record already has is refused, not moved. All or nothing. Safe to send again."""
        return self._run(OPERATIONS["LinkExternalIds"], {"kind": kind, "links": links, "source": source})

    def upsert_entity_models(self, *, models: list[EntityModelInput]) -> UpsertEntityModelsResult:
        """Make or change up to 100 custom entities and their fields, by key. A field can point at an entity sent in the same call. All or nothing."""
        return self._run(OPERATIONS["UpsertEntityModels"], {"models": models})

    def upsert_entity_records(
        self, *, model: str, records: list[EntityRecordInput], source: str | None = None
    ) -> UpsertEntityRecordsResult:
        """Send up to 100 records of one custom entity. All or nothing."""
        return self._run(OPERATIONS["UpsertEntityRecords"], {"model": model, "records": records, "source": source})


class AsyncOperations(ABC):
    @abstractmethod
    async def _run(self, operation: Operation, variables: dict[str, Any]) -> Any: ...

    @abstractmethod
    def _run_pages(self, operation: Operation, variables: dict[str, Any], max_pages: int) -> AsyncIterator[Any]: ...

    async def get_site(self) -> SiteFields | None:
        return await self._run(OPERATIONS["GetSite"], {})

    async def get_workcenter(self, *, id: str) -> WorkcenterFields | None:
        return await self._run(OPERATIONS["GetWorkcenter"], {"id": id})

    async def list_workcenters(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListWorkcentersResult:
        """Workcenter records at your site, oldest change first."""
        return await self._run(
            OPERATIONS["ListWorkcenters"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_workcenters(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> AsyncIterator[WorkcenterFields]:
        """Every record from list_workcenters, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListWorkcenters"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    async def get_station(self, *, id: str) -> StationFields | None:
        return await self._run(OPERATIONS["GetStation"], {"id": id})

    async def list_stations(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListStationsResult:
        """Station records at your site, oldest change first."""
        return await self._run(
            OPERATIONS["ListStations"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_stations(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> AsyncIterator[StationFields]:
        """Every record from list_stations, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListStations"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    async def get_customer(self, *, id: str) -> CustomerFields | None:
        return await self._run(OPERATIONS["GetCustomer"], {"id": id})

    async def list_customers(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListCustomersResult:
        """Customer records at your site, oldest change first."""
        return await self._run(
            OPERATIONS["ListCustomers"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_customers(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> AsyncIterator[CustomerFields]:
        """Every record from list_customers, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListCustomers"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    async def get_material(self, *, id: str) -> MaterialFields | None:
        return await self._run(OPERATIONS["GetMaterial"], {"id": id})

    async def list_materials(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListMaterialsResult:
        """Material records at your site, oldest change first."""
        return await self._run(
            OPERATIONS["ListMaterials"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_materials(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> AsyncIterator[MaterialFields]:
        """Every record from list_materials, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListMaterials"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    async def get_product(self, *, id: str) -> ProductFields | None:
        return await self._run(OPERATIONS["GetProduct"], {"id": id})

    async def list_products(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListProductsResult:
        """Product records at your site, oldest change first."""
        return await self._run(
            OPERATIONS["ListProducts"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_products(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> AsyncIterator[ProductFields]:
        """Every record from list_products, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListProducts"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    async def get_tool(self, *, id: str) -> ToolFields | None:
        return await self._run(OPERATIONS["GetTool"], {"id": id})

    async def list_tools(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListToolsResult:
        """Tool records at your site, oldest change first."""
        return await self._run(
            OPERATIONS["ListTools"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_tools(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> AsyncIterator[ToolFields]:
        """Every record from list_tools, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListTools"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    async def get_job(self, *, id: str) -> JobFields | None:
        return await self._run(OPERATIONS["GetJob"], {"id": id})

    async def list_jobs(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListJobsResult:
        """Job records at your site, oldest change first."""
        return await self._run(
            OPERATIONS["ListJobs"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_jobs(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> AsyncIterator[JobFields]:
        """Every record from list_jobs, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListJobs"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    async def get_order(self, *, id: str) -> OrderFields | None:
        return await self._run(OPERATIONS["GetOrder"], {"id": id})

    async def list_orders(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListOrdersResult:
        """Order records at your site, oldest change first."""
        return await self._run(
            OPERATIONS["ListOrders"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_orders(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> AsyncIterator[OrderFields]:
        """Every record from list_orders, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListOrders"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    async def get_production_run(self, *, id: str) -> ProductionRunFields | None:
        return await self._run(OPERATIONS["GetProductionRun"], {"id": id})

    async def list_production_runs(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListProductionRunsResult:
        """ProductionRun records at your site, oldest change first."""
        return await self._run(
            OPERATIONS["ListProductionRuns"],
            {"first": first, "after": after, "updatedSince": updated_since, "includeDeleted": include_deleted},
        )

    def list_all_production_runs(
        self,
        *,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> AsyncIterator[ProductionRunFields]:
        """Every record from list_production_runs, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListProductionRuns"],
            {"first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    async def get_station_lineup(self, *, id: str) -> GetStationLineupResult | None:
        return await self._run(OPERATIONS["GetStationLineup"], {"id": id})

    async def list_entity_models(self) -> list[EntityModelFields]:
        """The custom entities at your site, with their fields."""
        return await self._run(OPERATIONS["ListEntityModels"], {})

    async def get_entity_model(self, *, key: str) -> EntityModelFields | None:
        return await self._run(OPERATIONS["GetEntityModel"], {"key": key})

    async def get_entity_record(self, *, id: str) -> EntityRecordFields | None:
        return await self._run(OPERATIONS["GetEntityRecord"], {"id": id})

    async def list_entity_records(
        self,
        *,
        model: str,
        first: int | None = None,
        after: str | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
    ) -> ListEntityRecordsResult:
        """One custom entity's records, oldest change first."""
        return await self._run(
            OPERATIONS["ListEntityRecords"],
            {
                "model": model,
                "first": first,
                "after": after,
                "updatedSince": updated_since,
                "includeDeleted": include_deleted,
            },
        )

    def list_all_entity_records(
        self,
        *,
        model: str,
        first: int | None = None,
        updated_since: str | datetime | None = None,
        include_deleted: bool | None = None,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> AsyncIterator[EntityRecordFields]:
        """Every record from list_entity_records, page by page. See SPEC.md, Paging."""
        return self._run_pages(
            OPERATIONS["ListEntityRecords"],
            {"model": model, "first": first, "updatedSince": updated_since, "includeDeleted": include_deleted},
            max_pages,
        )

    async def list_webhooks(self) -> list[WebhookFields]:
        """This site's webhooks. Needs webhooks:write."""
        return await self._run(OPERATIONS["ListWebhooks"], {})

    async def list_webhook_deliveries(
        self, *, webhook_id: str, status: WebhookDeliveryStatus | None = None, first: int | None = None
    ) -> list[WebhookDeliveryFields]:
        """A webhook's deliveries, newest first. Needs webhooks:write."""
        return await self._run(
            OPERATIONS["ListWebhookDeliveries"], {"webhookId": webhook_id, "status": status, "first": first}
        )

    async def create_webhook(self, *, webhook: WebhookInput) -> CreateWebhookResult:
        """Make a webhook. Its signing secret is in the answer, and only there. Needs webhooks:write."""
        return await self._run(OPERATIONS["CreateWebhook"], {"webhook": webhook})

    async def update_webhook(self, *, id: str, webhook: WebhookUpdateInput) -> WebhookFields:
        """Change a webhook's URL, events or whether it's on. Needs webhooks:write."""
        return await self._run(OPERATIONS["UpdateWebhook"], {"id": id, "webhook": webhook})

    async def delete_webhook(self, *, id: str) -> bool:
        """Delete a webhook. Its retries stop. Needs webhooks:write."""
        return await self._run(OPERATIONS["DeleteWebhook"], {"id": id})

    async def rotate_webhook_secret(self, *, id: str) -> RotateWebhookSecretResult:
        """Give a webhook a new signing secret. The old one stops working now. Needs webhooks:write."""
        return await self._run(OPERATIONS["RotateWebhookSecret"], {"id": id})

    async def send_test_webhook(self, *, id: str) -> WebhookDeliveryFields:
        """Send a "webhook.test" event now, and see how your URL answered. Needs webhooks:write."""
        return await self._run(OPERATIONS["SendTestWebhook"], {"id": id})

    async def redeliver_webhook(self, *, delivery_id: str) -> WebhookDeliveryFields:
        """Send a delivery again, soon. Needs webhooks:write."""
        return await self._run(OPERATIONS["RedeliverWebhook"], {"deliveryId": delivery_id})

    async def upsert_workcenters(
        self, *, workcenters: list[WorkcenterInput], source: str | None = None
    ) -> UpsertWorkcentersResult:
        """Send up to 100 workcenters. All or nothing."""
        return await self._run(OPERATIONS["UpsertWorkcenters"], {"workcenters": workcenters, "source": source})

    async def upsert_stations(self, *, stations: list[StationInput], source: str | None = None) -> UpsertStationsResult:
        """Send up to 100 stations. All or nothing. Send workcenters first."""
        return await self._run(OPERATIONS["UpsertStations"], {"stations": stations, "source": source})

    async def upsert_customers(
        self, *, customers: list[CustomerUpsertInput], source: str | None = None
    ) -> UpsertCustomersResult:
        """Send up to 100 customers. All or nothing."""
        return await self._run(OPERATIONS["UpsertCustomers"], {"customers": customers, "source": source})

    async def upsert_materials(
        self, *, materials: list[MaterialInput], source: str | None = None
    ) -> UpsertMaterialsResult:
        """Send up to 100 materials. All or nothing: if one has a problem, none are saved."""
        return await self._run(OPERATIONS["UpsertMaterials"], {"materials": materials, "source": source})

    async def upsert_products(self, *, products: list[ProductInput], source: str | None = None) -> UpsertProductsResult:
        """Send up to 100 products, with their bills of materials. All or nothing: if one has a problem, none are saved. Send materials first."""
        return await self._run(OPERATIONS["UpsertProducts"], {"products": products, "source": source})

    async def upsert_tools(self, *, tools: list[ToolInput], source: str | None = None) -> UpsertToolsResult:
        """Send up to 100 tools, with their cavities. All or nothing."""
        return await self._run(OPERATIONS["UpsertTools"], {"tools": tools, "source": source})

    async def upsert_jobs(self, *, jobs: list[JobInput], source: str | None = None) -> UpsertJobsResult:
        """Send up to 100 jobs, with their tools and the products they make. All or nothing. Send tools and products first."""
        return await self._run(OPERATIONS["UpsertJobs"], {"jobs": jobs, "source": source})

    async def upsert_production_runs(
        self, *, runs: list[ProductionRunInput], source: str | None = None
    ) -> UpsertProductionRunsResult:
        """Send up to 100 runs to stations' lineups. A new run goes to the end of its station's queue; an update never moves it, because the plant can reorder runs. Changing a queued run's station or job takes it off and adds it again at the end. The lineup's rules are the same as in IMM: a running run can change its counts and dates only, and a closed one nothing. Safe to send again."""
        return await self._run(OPERATIONS["UpsertProductionRuns"], {"runs": runs, "source": source})

    async def upsert_order(self, *, order: OrderInput, source: str | None = None) -> UpsertOrderResult:
        """Send one order, with its customer and lines. Safe to send again: the same order gives the same result."""
        return await self._run(OPERATIONS["UpsertOrder"], {"order": order, "source": source})

    async def sequence_lineup(
        self, *, station: str, runs: list[str], source: str | None = None
    ) -> SequenceLineupResult:
        """Put runs in order at one station, by your ids. They take the places they already hold in its queue, in the order given, and every other run stays where it is. Only queued runs. Safe to send again."""
        return await self._run(OPERATIONS["SequenceLineup"], {"station": station, "runs": runs, "source": source})

    async def link_external_ids(
        self, *, kind: ExternalIdKind, links: list[ExternalIdLinkInput], source: str | None = None
    ) -> LinkExternalIdsResult:
        """Give up to 100 records made in IMM your own ids, by their id in IMM. From then on you can use your id wherever the API takes theirs, and renaming them in IMM changes nothing. An id another record already has is refused, not moved. All or nothing. Safe to send again."""
        return await self._run(OPERATIONS["LinkExternalIds"], {"kind": kind, "links": links, "source": source})

    async def upsert_entity_models(self, *, models: list[EntityModelInput]) -> UpsertEntityModelsResult:
        """Make or change up to 100 custom entities and their fields, by key. A field can point at an entity sent in the same call. All or nothing."""
        return await self._run(OPERATIONS["UpsertEntityModels"], {"models": models})

    async def upsert_entity_records(
        self, *, model: str, records: list[EntityRecordInput], source: str | None = None
    ) -> UpsertEntityRecordsResult:
        """Send up to 100 records of one custom entity. All or nothing."""
        return await self._run(
            OPERATIONS["UpsertEntityRecords"], {"model": model, "records": records, "source": source}
        )
