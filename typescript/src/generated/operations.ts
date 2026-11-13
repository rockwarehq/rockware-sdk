// Made by scripts/generate.ts from the repo's schema/, operations/ and behavior.json. Don't edit it.

import type * as T from "./types.js";
import type { CallOptions, Operation, PageOptions } from "../operation.js";

export const OPERATIONS = {
  GetSite: {
    name: "GetSite",
    root: "site",
    mutation: false,
    safeToRepeat: true,
    document: "query GetSite {\n  site {\n    ...SiteFields\n  }\n}\n\nfragment SiteFields on Site {\n  id\n  name\n  description\n  timezone\n  updatedAt\n}",
  },
  GetWorkcenter: {
    name: "GetWorkcenter",
    root: "workcenter",
    mutation: false,
    safeToRepeat: true,
    document: "query GetWorkcenter($id: ID!) {\n  workcenter(id: $id) {\n    ...WorkcenterFields\n  }\n}\n\nfragment WorkcenterFields on Workcenter {\n  id\n  name\n  description\n  parentId\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListWorkcenters: {
    name: "ListWorkcenters",
    root: "workcenters",
    mutation: false,
    safeToRepeat: true,
    document: "query ListWorkcenters($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  workcenters(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...WorkcenterFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment WorkcenterFields on Workcenter {\n  id\n  name\n  description\n  parentId\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  GetStation: {
    name: "GetStation",
    root: "station",
    mutation: false,
    safeToRepeat: true,
    document: "query GetStation($id: ID!) {\n  station(id: $id) {\n    ...StationFields\n  }\n}\n\nfragment StationFields on Station {\n  id\n  name\n  description\n  sortOrder\n  workcenterId\n  workcenter {\n    id\n    name\n  }\n  currentJobId\n  currentJob {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListStations: {
    name: "ListStations",
    root: "stations",
    mutation: false,
    safeToRepeat: true,
    document: "query ListStations($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  stations(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...StationFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment StationFields on Station {\n  id\n  name\n  description\n  sortOrder\n  workcenterId\n  workcenter {\n    id\n    name\n  }\n  currentJobId\n  currentJob {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  GetCustomer: {
    name: "GetCustomer",
    root: "customer",
    mutation: false,
    safeToRepeat: true,
    document: "query GetCustomer($id: ID!) {\n  customer(id: $id) {\n    ...CustomerFields\n  }\n}\n\nfragment CustomerFields on Customer {\n  id\n  name\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListCustomers: {
    name: "ListCustomers",
    root: "customers",
    mutation: false,
    safeToRepeat: true,
    document: "query ListCustomers($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  customers(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...CustomerFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment CustomerFields on Customer {\n  id\n  name\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  GetMaterial: {
    name: "GetMaterial",
    root: "material",
    mutation: false,
    safeToRepeat: true,
    document: "query GetMaterial($id: ID!) {\n  material(id: $id) {\n    ...MaterialFields\n  }\n}\n\nfragment MaterialFields on Material {\n  id\n  materialNumber\n  name\n  description\n  classification\n  shortCode\n  externalNumber\n  unitCost\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListMaterials: {
    name: "ListMaterials",
    root: "materials",
    mutation: false,
    safeToRepeat: true,
    document: "query ListMaterials($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  materials(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...MaterialFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment MaterialFields on Material {\n  id\n  materialNumber\n  name\n  description\n  classification\n  shortCode\n  externalNumber\n  unitCost\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  GetProduct: {
    name: "GetProduct",
    root: "product",
    mutation: false,
    safeToRepeat: true,
    document: "query GetProduct($id: ID!) {\n  product(id: $id) {\n    ...ProductFields\n  }\n}\n\nfragment ProductFields on Product {\n  id\n  sku\n  name\n  description\n  externalSku\n  itemCost\n  weight\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListProducts: {
    name: "ListProducts",
    root: "products",
    mutation: false,
    safeToRepeat: true,
    document: "query ListProducts($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  products(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...ProductFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment ProductFields on Product {\n  id\n  sku\n  name\n  description\n  externalSku\n  itemCost\n  weight\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  GetTool: {
    name: "GetTool",
    root: "tool",
    mutation: false,
    safeToRepeat: true,
    document: "query GetTool($id: ID!) {\n  tool(id: $id) {\n    ...ToolFields\n  }\n}\n\nfragment ToolFields on Tool {\n  id\n  name\n  description\n  cavityCount\n  cavities {\n    id\n    name\n    position\n  }\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListTools: {
    name: "ListTools",
    root: "tools",
    mutation: false,
    safeToRepeat: true,
    document: "query ListTools($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  tools(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...ToolFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment ToolFields on Tool {\n  id\n  name\n  description\n  cavityCount\n  cavities {\n    id\n    name\n    position\n  }\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  GetJob: {
    name: "GetJob",
    root: "job",
    mutation: false,
    safeToRepeat: true,
    document: "query GetJob($id: ID!) {\n  job(id: $id) {\n    ...JobFields\n  }\n}\n\nfragment JobFields on Job {\n  id\n  name\n  description\n  version\n  standardRate\n  standardRateUnit\n  standardRatePeriod\n  standardCycle\n  standardQuantity\n  productsPerCycle\n  profileId\n  tools {\n    id\n    name\n  }\n  items {\n    id\n    quantity\n    isActive\n    cavityId\n    product {\n      id\n      sku\n    }\n    tool {\n      id\n      name\n    }\n  }\n  eligibleStations {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListJobs: {
    name: "ListJobs",
    root: "jobs",
    mutation: false,
    safeToRepeat: true,
    document: "query ListJobs($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  jobs(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...JobFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment JobFields on Job {\n  id\n  name\n  description\n  version\n  standardRate\n  standardRateUnit\n  standardRatePeriod\n  standardCycle\n  standardQuantity\n  productsPerCycle\n  profileId\n  tools {\n    id\n    name\n  }\n  items {\n    id\n    quantity\n    isActive\n    cavityId\n    product {\n      id\n      sku\n    }\n    tool {\n      id\n      name\n    }\n  }\n  eligibleStations {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  GetOrder: {
    name: "GetOrder",
    root: "order",
    mutation: false,
    safeToRepeat: true,
    document: "query GetOrder($id: ID!) {\n  order(id: $id) {\n    ...OrderFields\n  }\n}\n\nfragment OrderFields on Order {\n  id\n  orderNumber\n  poNumber\n  status\n  notes\n  customerId\n  customer {\n    id\n    name\n  }\n  defaultTargetQuantity\n  startDate\n  dueDate\n  openedAt\n  completedAt\n  cancelledAt\n  lines {\n    id\n    productId\n    product {\n      id\n      sku\n    }\n    targetQuantity\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListOrders: {
    name: "ListOrders",
    root: "orders",
    mutation: false,
    safeToRepeat: true,
    document: "query ListOrders($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  orders(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...OrderFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment OrderFields on Order {\n  id\n  orderNumber\n  poNumber\n  status\n  notes\n  customerId\n  customer {\n    id\n    name\n  }\n  defaultTargetQuantity\n  startDate\n  dueDate\n  openedAt\n  completedAt\n  cancelledAt\n  lines {\n    id\n    productId\n    product {\n      id\n      sku\n    }\n    targetQuantity\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  GetProductionRun: {
    name: "GetProductionRun",
    root: "productionRun",
    mutation: false,
    safeToRepeat: true,
    document: "query GetProductionRun($id: ID!) {\n  productionRun(id: $id) {\n    ...ProductionRunFields\n  }\n}\n\nfragment ProductionRunFields on ProductionRun {\n  id\n  status\n  rank\n  stationId\n  station {\n    id\n    name\n  }\n  workcenterId\n  jobId\n  job {\n    id\n    name\n  }\n  parts {\n    productId\n    product {\n      id\n      sku\n    }\n    perCycle\n    requiredGood\n    goodCount\n    scrapCount\n    metAt\n  }\n  startBy\n  endBy\n  startByMissed\n  endByMissed\n  plannedStart\n  plannedEnd\n  plannedBusinessDate\n  plannedShiftName\n  plannedChangeoverMinutes\n  actualChangeoverMinutes\n  runStartedAt\n  quantityMetAt\n  closedAt\n  closedBusinessDate\n  closeReason\n  skipCount\n  jobChangedAt\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListProductionRuns: {
    name: "ListProductionRuns",
    root: "productionRuns",
    mutation: false,
    safeToRepeat: true,
    document: "query ListProductionRuns($first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  productionRuns(\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...ProductionRunFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment ProductionRunFields on ProductionRun {\n  id\n  status\n  rank\n  stationId\n  station {\n    id\n    name\n  }\n  workcenterId\n  jobId\n  job {\n    id\n    name\n  }\n  parts {\n    productId\n    product {\n      id\n      sku\n    }\n    perCycle\n    requiredGood\n    goodCount\n    scrapCount\n    metAt\n  }\n  startBy\n  endBy\n  startByMissed\n  endByMissed\n  plannedStart\n  plannedEnd\n  plannedBusinessDate\n  plannedShiftName\n  plannedChangeoverMinutes\n  actualChangeoverMinutes\n  runStartedAt\n  quantityMetAt\n  closedAt\n  closedBusinessDate\n  closeReason\n  skipCount\n  jobChangedAt\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  GetStationLineup: {
    name: "GetStationLineup",
    root: "station",
    mutation: false,
    safeToRepeat: true,
    document: "query GetStationLineup($id: ID!) {\n  station(id: $id) {\n    id\n    name\n    lineup {\n      position\n      predictedChangeoverStart\n      predictedStart\n      predictedEnd\n      startByAtRisk\n      endByAtRisk\n      progress {\n        productId\n        requiredGood\n        good\n        scrap\n      }\n      run {\n        ...ProductionRunFields\n      }\n    }\n  }\n}\n\nfragment ProductionRunFields on ProductionRun {\n  id\n  status\n  rank\n  stationId\n  station {\n    id\n    name\n  }\n  workcenterId\n  jobId\n  job {\n    id\n    name\n  }\n  parts {\n    productId\n    product {\n      id\n      sku\n    }\n    perCycle\n    requiredGood\n    goodCount\n    scrapCount\n    metAt\n  }\n  startBy\n  endBy\n  startByMissed\n  endByMissed\n  plannedStart\n  plannedEnd\n  plannedBusinessDate\n  plannedShiftName\n  plannedChangeoverMinutes\n  actualChangeoverMinutes\n  runStartedAt\n  quantityMetAt\n  closedAt\n  closedBusinessDate\n  closeReason\n  skipCount\n  jobChangedAt\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListEntityModels: {
    name: "ListEntityModels",
    root: "entityModels",
    mutation: false,
    safeToRepeat: true,
    document: "query ListEntityModels {\n  entityModels {\n    ...EntityModelFields\n  }\n}\n\nfragment EntityModelFields on EntityModel {\n  id\n  key\n  label\n  description\n  version\n  fields {\n    key\n    label\n    description\n    type\n    required\n    isList\n    refModel\n    options {\n      value\n      label\n    }\n  }\n  createdAt\n  updatedAt\n}",
  },
  GetEntityModel: {
    name: "GetEntityModel",
    root: "entityModel",
    mutation: false,
    safeToRepeat: true,
    document: "query GetEntityModel($key: String!) {\n  entityModel(key: $key) {\n    ...EntityModelFields\n  }\n}\n\nfragment EntityModelFields on EntityModel {\n  id\n  key\n  label\n  description\n  version\n  fields {\n    key\n    label\n    description\n    type\n    required\n    isList\n    refModel\n    options {\n      value\n      label\n    }\n  }\n  createdAt\n  updatedAt\n}",
  },
  GetEntityRecord: {
    name: "GetEntityRecord",
    root: "entityRecord",
    mutation: false,
    safeToRepeat: true,
    document: "query GetEntityRecord($id: ID!) {\n  entityRecord(id: $id) {\n    ...EntityRecordFields\n  }\n}\n\nfragment EntityRecordFields on EntityRecord {\n  id\n  model\n  name\n  values\n  deleted\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListEntityRecords: {
    name: "ListEntityRecords",
    root: "entityRecords",
    mutation: false,
    safeToRepeat: true,
    document: "query ListEntityRecords($model: String!, $first: Int, $after: String, $updatedSince: DateTime, $includeDeleted: Boolean) {\n  entityRecords(\n    model: $model\n    first: $first\n    after: $after\n    updatedSince: $updatedSince\n    includeDeleted: $includeDeleted\n  ) {\n    nodes {\n      ...EntityRecordFields\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment EntityRecordFields on EntityRecord {\n  id\n  model\n  name\n  values\n  deleted\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}",
  },
  ListWebhooks: {
    name: "ListWebhooks",
    root: "webhooks",
    mutation: false,
    safeToRepeat: true,
    document: "query ListWebhooks {\n  webhooks {\n    ...WebhookFields\n  }\n}\n\nfragment WebhookFields on Webhook {\n  id\n  url\n  events\n  enabled\n  createdAt\n  updatedAt\n}",
  },
  ListWebhookDeliveries: {
    name: "ListWebhookDeliveries",
    root: "webhookDeliveries",
    mutation: false,
    safeToRepeat: true,
    document: "query ListWebhookDeliveries($webhookId: ID!, $status: WebhookDeliveryStatus, $first: Int) {\n  webhookDeliveries(webhookId: $webhookId, status: $status, first: $first) {\n    ...WebhookDeliveryFields\n  }\n}\n\nfragment WebhookDeliveryFields on WebhookDelivery {\n  id\n  eventId\n  type\n  status\n  attempts\n  responseStatus\n  error\n  startedAt\n  finishedAt\n  nextAttemptAt\n}",
  },
  CreateWebhook: {
    name: "CreateWebhook",
    root: "createWebhook",
    mutation: true,
    safeToRepeat: false,
    document: "mutation CreateWebhook($webhook: WebhookInput!) {\n  createWebhook(webhook: $webhook) {\n    secret\n    webhook {\n      ...WebhookFields\n    }\n  }\n}\n\nfragment WebhookFields on Webhook {\n  id\n  url\n  events\n  enabled\n  createdAt\n  updatedAt\n}",
  },
  UpdateWebhook: {
    name: "UpdateWebhook",
    root: "updateWebhook",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpdateWebhook($id: ID!, $webhook: WebhookUpdateInput!) {\n  updateWebhook(id: $id, webhook: $webhook) {\n    ...WebhookFields\n  }\n}\n\nfragment WebhookFields on Webhook {\n  id\n  url\n  events\n  enabled\n  createdAt\n  updatedAt\n}",
  },
  DeleteWebhook: {
    name: "DeleteWebhook",
    root: "deleteWebhook",
    mutation: true,
    safeToRepeat: false,
    document: "mutation DeleteWebhook($id: ID!) {\n  deleteWebhook(id: $id)\n}",
  },
  RotateWebhookSecret: {
    name: "RotateWebhookSecret",
    root: "rotateWebhookSecret",
    mutation: true,
    safeToRepeat: false,
    document: "mutation RotateWebhookSecret($id: ID!) {\n  rotateWebhookSecret(id: $id) {\n    secret\n    webhook {\n      ...WebhookFields\n    }\n  }\n}\n\nfragment WebhookFields on Webhook {\n  id\n  url\n  events\n  enabled\n  createdAt\n  updatedAt\n}",
  },
  SendTestWebhook: {
    name: "SendTestWebhook",
    root: "sendTestWebhook",
    mutation: true,
    safeToRepeat: false,
    document: "mutation SendTestWebhook($id: ID!) {\n  sendTestWebhook(id: $id) {\n    ...WebhookDeliveryFields\n  }\n}\n\nfragment WebhookDeliveryFields on WebhookDelivery {\n  id\n  eventId\n  type\n  status\n  attempts\n  responseStatus\n  error\n  startedAt\n  finishedAt\n  nextAttemptAt\n}",
  },
  RedeliverWebhook: {
    name: "RedeliverWebhook",
    root: "redeliverWebhook",
    mutation: true,
    safeToRepeat: false,
    document: "mutation RedeliverWebhook($deliveryId: ID!) {\n  redeliverWebhook(deliveryId: $deliveryId) {\n    ...WebhookDeliveryFields\n  }\n}\n\nfragment WebhookDeliveryFields on WebhookDelivery {\n  id\n  eventId\n  type\n  status\n  attempts\n  responseStatus\n  error\n  startedAt\n  finishedAt\n  nextAttemptAt\n}",
  },
  UpsertWorkcenters: {
    name: "UpsertWorkcenters",
    root: "upsertWorkcenters",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpsertWorkcenters($workcenters: [WorkcenterInput!]!, $source: String) {\n  upsertWorkcenters(workcenters: $workcenters, source: $source) {\n    results {\n      externalId\n      action\n      workcenter {\n        ...WorkcenterFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment WorkcenterFields on Workcenter {\n  id\n  name\n  description\n  parentId\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  UpsertStations: {
    name: "UpsertStations",
    root: "upsertStations",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpsertStations($stations: [StationInput!]!, $source: String) {\n  upsertStations(stations: $stations, source: $source) {\n    results {\n      externalId\n      action\n      station {\n        ...StationFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment StationFields on Station {\n  id\n  name\n  description\n  sortOrder\n  workcenterId\n  workcenter {\n    id\n    name\n  }\n  currentJobId\n  currentJob {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  UpsertCustomers: {
    name: "UpsertCustomers",
    root: "upsertCustomers",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpsertCustomers($customers: [CustomerUpsertInput!]!, $source: String) {\n  upsertCustomers(customers: $customers, source: $source) {\n    results {\n      externalId\n      action\n      customer {\n        ...CustomerFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment CustomerFields on Customer {\n  id\n  name\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  UpsertMaterials: {
    name: "UpsertMaterials",
    root: "upsertMaterials",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpsertMaterials($materials: [MaterialInput!]!, $source: String) {\n  upsertMaterials(materials: $materials, source: $source) {\n    results {\n      externalId\n      action\n      material {\n        ...MaterialFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment MaterialFields on Material {\n  id\n  materialNumber\n  name\n  description\n  classification\n  shortCode\n  externalNumber\n  unitCost\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  UpsertProducts: {
    name: "UpsertProducts",
    root: "upsertProducts",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpsertProducts($products: [ProductInput!]!, $source: String) {\n  upsertProducts(products: $products, source: $source) {\n    results {\n      externalId\n      action\n      product {\n        ...ProductFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment ProductFields on Product {\n  id\n  sku\n  name\n  description\n  externalSku\n  itemCost\n  weight\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  UpsertTools: {
    name: "UpsertTools",
    root: "upsertTools",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpsertTools($tools: [ToolInput!]!, $source: String) {\n  upsertTools(tools: $tools, source: $source) {\n    results {\n      externalId\n      action\n      tool {\n        ...ToolFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment ToolFields on Tool {\n  id\n  name\n  description\n  cavityCount\n  cavities {\n    id\n    name\n    position\n  }\n  version\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  UpsertJobs: {
    name: "UpsertJobs",
    root: "upsertJobs",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpsertJobs($jobs: [JobInput!]!, $source: String) {\n  upsertJobs(jobs: $jobs, source: $source) {\n    results {\n      externalId\n      action\n      job {\n        ...JobFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment JobFields on Job {\n  id\n  name\n  description\n  version\n  standardRate\n  standardRateUnit\n  standardRatePeriod\n  standardCycle\n  standardQuantity\n  productsPerCycle\n  profileId\n  tools {\n    id\n    name\n  }\n  items {\n    id\n    quantity\n    isActive\n    cavityId\n    product {\n      id\n      sku\n    }\n    tool {\n      id\n      name\n    }\n  }\n  eligibleStations {\n    id\n    name\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  archivedAt\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  UpsertProductionRuns: {
    name: "UpsertProductionRuns",
    root: "upsertProductionRuns",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpsertProductionRuns($runs: [ProductionRunInput!]!, $source: String) {\n  upsertProductionRuns(runs: $runs, source: $source) {\n    results {\n      externalId\n      action\n      run {\n        ...ProductionRunFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment ProductionRunFields on ProductionRun {\n  id\n  status\n  rank\n  stationId\n  station {\n    id\n    name\n  }\n  workcenterId\n  jobId\n  job {\n    id\n    name\n  }\n  parts {\n    productId\n    product {\n      id\n      sku\n    }\n    perCycle\n    requiredGood\n    goodCount\n    scrapCount\n    metAt\n  }\n  startBy\n  endBy\n  startByMissed\n  endByMissed\n  plannedStart\n  plannedEnd\n  plannedBusinessDate\n  plannedShiftName\n  plannedChangeoverMinutes\n  actualChangeoverMinutes\n  runStartedAt\n  quantityMetAt\n  closedAt\n  closedBusinessDate\n  closeReason\n  skipCount\n  jobChangedAt\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  UpsertOrder: {
    name: "UpsertOrder",
    root: "upsertOrder",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpsertOrder($order: OrderInput!, $source: String) {\n  upsertOrder(order: $order, source: $source) {\n    action\n    order {\n      ...OrderFields\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment OrderFields on Order {\n  id\n  orderNumber\n  poNumber\n  status\n  notes\n  customerId\n  customer {\n    id\n    name\n  }\n  defaultTargetQuantity\n  startDate\n  dueDate\n  openedAt\n  completedAt\n  cancelledAt\n  lines {\n    id\n    productId\n    product {\n      id\n      sku\n    }\n    targetQuantity\n  }\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n  deletedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  SequenceLineup: {
    name: "SequenceLineup",
    root: "sequenceLineup",
    mutation: true,
    safeToRepeat: true,
    document: "mutation SequenceLineup($station: String!, $runs: [String!]!, $source: String) {\n  sequenceLineup(station: $station, runs: $runs, source: $source) {\n    action\n    station {\n      id\n      name\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  LinkExternalIds: {
    name: "LinkExternalIds",
    root: "linkExternalIds",
    mutation: true,
    safeToRepeat: true,
    document: "mutation LinkExternalIds($kind: ExternalIdKind!, $links: [ExternalIdLinkInput!]!, $source: String) {\n  linkExternalIds(kind: $kind, links: $links, source: $source) {\n    results {\n      id\n      externalId\n      action\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  UpsertEntityModels: {
    name: "UpsertEntityModels",
    root: "upsertEntityModels",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpsertEntityModels($models: [EntityModelInput!]!) {\n  upsertEntityModels(models: $models) {\n    results {\n      key\n      action\n      model {\n        ...EntityModelFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment EntityModelFields on EntityModel {\n  id\n  key\n  label\n  description\n  version\n  fields {\n    key\n    label\n    description\n    type\n    required\n    isList\n    refModel\n    options {\n      value\n      label\n    }\n  }\n  createdAt\n  updatedAt\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
  UpsertEntityRecords: {
    name: "UpsertEntityRecords",
    root: "upsertEntityRecords",
    mutation: true,
    safeToRepeat: true,
    document: "mutation UpsertEntityRecords($model: String!, $records: [EntityRecordInput!]!, $source: String) {\n  upsertEntityRecords(model: $model, records: $records, source: $source) {\n    results {\n      externalId\n      action\n      record {\n        ...EntityRecordFields\n      }\n    }\n    errors {\n      ...UpsertErrorFields\n    }\n  }\n}\n\nfragment EntityRecordFields on EntityRecord {\n  id\n  model\n  name\n  values\n  deleted\n  externalIds {\n    ...ExternalIdFields\n  }\n  createdAt\n  updatedAt\n}\n\nfragment ExternalIdFields on ExternalId {\n  id\n  source\n}\n\nfragment UpsertErrorFields on UpsertError {\n  code\n  field\n  message\n}",
  },
} as const satisfies Record<string, Operation>;

export type OperationName = keyof typeof OPERATIONS;

/** Operations that return a connection, which listAll… pages through. */
export const PAGEABLE: readonly OperationName[] = ["ListWorkcenters", "ListStations", "ListCustomers", "ListMaterials", "ListProducts", "ListTools", "ListJobs", "ListOrders", "ListProductionRuns", "ListEntityRecords"];

/** One method per operation in operations/. RockwareClient fills in how they're sent. */
export abstract class Operations {
  protected abstract run<R>(operation: Operation, variables: object | undefined, options?: CallOptions): Promise<R>;
  protected abstract runPages<N>(operation: Operation, variables: object, options?: PageOptions): AsyncGenerator<N>;

  getSite(options?: CallOptions): Promise<T.GetSiteQuery["site"]> {
    return this.run(OPERATIONS.GetSite, undefined, options);
  }

  getWorkcenter(variables: T.GetWorkcenterQueryVariables, options?: CallOptions): Promise<T.GetWorkcenterQuery["workcenter"]> {
    return this.run(OPERATIONS.GetWorkcenter, variables, options);
  }

  /**
   * Workcenter records at your site, oldest change first.
   */
  listWorkcenters(variables: T.ListWorkcentersQueryVariables = {}, options?: CallOptions): Promise<T.ListWorkcentersQuery["workcenters"]> {
    return this.run(OPERATIONS.ListWorkcenters, variables, options);
  }

  /** Every record from listWorkcenters, page by page. See SPEC.md, Paging. */
  listAllWorkcenters(variables: Omit<T.ListWorkcentersQueryVariables, "after"> = {}, options?: PageOptions): AsyncGenerator<T.ListWorkcentersQuery["workcenters"]["nodes"][number]> {
    return this.runPages(OPERATIONS.ListWorkcenters, variables, options);
  }

  getStation(variables: T.GetStationQueryVariables, options?: CallOptions): Promise<T.GetStationQuery["station"]> {
    return this.run(OPERATIONS.GetStation, variables, options);
  }

  /**
   * Station records at your site, oldest change first.
   */
  listStations(variables: T.ListStationsQueryVariables = {}, options?: CallOptions): Promise<T.ListStationsQuery["stations"]> {
    return this.run(OPERATIONS.ListStations, variables, options);
  }

  /** Every record from listStations, page by page. See SPEC.md, Paging. */
  listAllStations(variables: Omit<T.ListStationsQueryVariables, "after"> = {}, options?: PageOptions): AsyncGenerator<T.ListStationsQuery["stations"]["nodes"][number]> {
    return this.runPages(OPERATIONS.ListStations, variables, options);
  }

  getCustomer(variables: T.GetCustomerQueryVariables, options?: CallOptions): Promise<T.GetCustomerQuery["customer"]> {
    return this.run(OPERATIONS.GetCustomer, variables, options);
  }

  /**
   * Customer records at your site, oldest change first.
   */
  listCustomers(variables: T.ListCustomersQueryVariables = {}, options?: CallOptions): Promise<T.ListCustomersQuery["customers"]> {
    return this.run(OPERATIONS.ListCustomers, variables, options);
  }

  /** Every record from listCustomers, page by page. See SPEC.md, Paging. */
  listAllCustomers(variables: Omit<T.ListCustomersQueryVariables, "after"> = {}, options?: PageOptions): AsyncGenerator<T.ListCustomersQuery["customers"]["nodes"][number]> {
    return this.runPages(OPERATIONS.ListCustomers, variables, options);
  }

  getMaterial(variables: T.GetMaterialQueryVariables, options?: CallOptions): Promise<T.GetMaterialQuery["material"]> {
    return this.run(OPERATIONS.GetMaterial, variables, options);
  }

  /**
   * Material records at your site, oldest change first.
   */
  listMaterials(variables: T.ListMaterialsQueryVariables = {}, options?: CallOptions): Promise<T.ListMaterialsQuery["materials"]> {
    return this.run(OPERATIONS.ListMaterials, variables, options);
  }

  /** Every record from listMaterials, page by page. See SPEC.md, Paging. */
  listAllMaterials(variables: Omit<T.ListMaterialsQueryVariables, "after"> = {}, options?: PageOptions): AsyncGenerator<T.ListMaterialsQuery["materials"]["nodes"][number]> {
    return this.runPages(OPERATIONS.ListMaterials, variables, options);
  }

  getProduct(variables: T.GetProductQueryVariables, options?: CallOptions): Promise<T.GetProductQuery["product"]> {
    return this.run(OPERATIONS.GetProduct, variables, options);
  }

  /**
   * Product records at your site, oldest change first.
   */
  listProducts(variables: T.ListProductsQueryVariables = {}, options?: CallOptions): Promise<T.ListProductsQuery["products"]> {
    return this.run(OPERATIONS.ListProducts, variables, options);
  }

  /** Every record from listProducts, page by page. See SPEC.md, Paging. */
  listAllProducts(variables: Omit<T.ListProductsQueryVariables, "after"> = {}, options?: PageOptions): AsyncGenerator<T.ListProductsQuery["products"]["nodes"][number]> {
    return this.runPages(OPERATIONS.ListProducts, variables, options);
  }

  getTool(variables: T.GetToolQueryVariables, options?: CallOptions): Promise<T.GetToolQuery["tool"]> {
    return this.run(OPERATIONS.GetTool, variables, options);
  }

  /**
   * Tool records at your site, oldest change first.
   */
  listTools(variables: T.ListToolsQueryVariables = {}, options?: CallOptions): Promise<T.ListToolsQuery["tools"]> {
    return this.run(OPERATIONS.ListTools, variables, options);
  }

  /** Every record from listTools, page by page. See SPEC.md, Paging. */
  listAllTools(variables: Omit<T.ListToolsQueryVariables, "after"> = {}, options?: PageOptions): AsyncGenerator<T.ListToolsQuery["tools"]["nodes"][number]> {
    return this.runPages(OPERATIONS.ListTools, variables, options);
  }

  getJob(variables: T.GetJobQueryVariables, options?: CallOptions): Promise<T.GetJobQuery["job"]> {
    return this.run(OPERATIONS.GetJob, variables, options);
  }

  /**
   * Job records at your site, oldest change first.
   */
  listJobs(variables: T.ListJobsQueryVariables = {}, options?: CallOptions): Promise<T.ListJobsQuery["jobs"]> {
    return this.run(OPERATIONS.ListJobs, variables, options);
  }

  /** Every record from listJobs, page by page. See SPEC.md, Paging. */
  listAllJobs(variables: Omit<T.ListJobsQueryVariables, "after"> = {}, options?: PageOptions): AsyncGenerator<T.ListJobsQuery["jobs"]["nodes"][number]> {
    return this.runPages(OPERATIONS.ListJobs, variables, options);
  }

  getOrder(variables: T.GetOrderQueryVariables, options?: CallOptions): Promise<T.GetOrderQuery["order"]> {
    return this.run(OPERATIONS.GetOrder, variables, options);
  }

  /**
   * Order records at your site, oldest change first.
   */
  listOrders(variables: T.ListOrdersQueryVariables = {}, options?: CallOptions): Promise<T.ListOrdersQuery["orders"]> {
    return this.run(OPERATIONS.ListOrders, variables, options);
  }

  /** Every record from listOrders, page by page. See SPEC.md, Paging. */
  listAllOrders(variables: Omit<T.ListOrdersQueryVariables, "after"> = {}, options?: PageOptions): AsyncGenerator<T.ListOrdersQuery["orders"]["nodes"][number]> {
    return this.runPages(OPERATIONS.ListOrders, variables, options);
  }

  getProductionRun(variables: T.GetProductionRunQueryVariables, options?: CallOptions): Promise<T.GetProductionRunQuery["productionRun"]> {
    return this.run(OPERATIONS.GetProductionRun, variables, options);
  }

  /**
   * ProductionRun records at your site, oldest change first.
   */
  listProductionRuns(variables: T.ListProductionRunsQueryVariables = {}, options?: CallOptions): Promise<T.ListProductionRunsQuery["productionRuns"]> {
    return this.run(OPERATIONS.ListProductionRuns, variables, options);
  }

  /** Every record from listProductionRuns, page by page. See SPEC.md, Paging. */
  listAllProductionRuns(variables: Omit<T.ListProductionRunsQueryVariables, "after"> = {}, options?: PageOptions): AsyncGenerator<T.ListProductionRunsQuery["productionRuns"]["nodes"][number]> {
    return this.runPages(OPERATIONS.ListProductionRuns, variables, options);
  }

  getStationLineup(variables: T.GetStationLineupQueryVariables, options?: CallOptions): Promise<T.GetStationLineupQuery["station"]> {
    return this.run(OPERATIONS.GetStationLineup, variables, options);
  }

  /**
   * The custom entities at your site, with their fields.
   */
  listEntityModels(options?: CallOptions): Promise<T.ListEntityModelsQuery["entityModels"]> {
    return this.run(OPERATIONS.ListEntityModels, undefined, options);
  }

  getEntityModel(variables: T.GetEntityModelQueryVariables, options?: CallOptions): Promise<T.GetEntityModelQuery["entityModel"]> {
    return this.run(OPERATIONS.GetEntityModel, variables, options);
  }

  getEntityRecord(variables: T.GetEntityRecordQueryVariables, options?: CallOptions): Promise<T.GetEntityRecordQuery["entityRecord"]> {
    return this.run(OPERATIONS.GetEntityRecord, variables, options);
  }

  /**
   * One custom entity's records, oldest change first.
   */
  listEntityRecords(variables: T.ListEntityRecordsQueryVariables, options?: CallOptions): Promise<T.ListEntityRecordsQuery["entityRecords"]> {
    return this.run(OPERATIONS.ListEntityRecords, variables, options);
  }

  /** Every record from listEntityRecords, page by page. See SPEC.md, Paging. */
  listAllEntityRecords(variables: Omit<T.ListEntityRecordsQueryVariables, "after">, options?: PageOptions): AsyncGenerator<T.ListEntityRecordsQuery["entityRecords"]["nodes"][number]> {
    return this.runPages(OPERATIONS.ListEntityRecords, variables, options);
  }

  /**
   * This site's webhooks. Needs webhooks:write.
   */
  listWebhooks(options?: CallOptions): Promise<T.ListWebhooksQuery["webhooks"]> {
    return this.run(OPERATIONS.ListWebhooks, undefined, options);
  }

  /**
   * A webhook's deliveries, newest first. Needs webhooks:write.
   */
  listWebhookDeliveries(variables: T.ListWebhookDeliveriesQueryVariables, options?: CallOptions): Promise<T.ListWebhookDeliveriesQuery["webhookDeliveries"]> {
    return this.run(OPERATIONS.ListWebhookDeliveries, variables, options);
  }

  /**
   * Make a webhook. Its signing secret is in the answer, and only there. Needs webhooks:write.
   */
  createWebhook(variables: T.CreateWebhookMutationVariables, options?: CallOptions): Promise<T.CreateWebhookMutation["createWebhook"]> {
    return this.run(OPERATIONS.CreateWebhook, variables, options);
  }

  /**
   * Change a webhook's URL, events or whether it's on. Needs webhooks:write.
   */
  updateWebhook(variables: T.UpdateWebhookMutationVariables, options?: CallOptions): Promise<T.UpdateWebhookMutation["updateWebhook"]> {
    return this.run(OPERATIONS.UpdateWebhook, variables, options);
  }

  /**
   * Delete a webhook. Its retries stop. Needs webhooks:write.
   */
  deleteWebhook(variables: T.DeleteWebhookMutationVariables, options?: CallOptions): Promise<T.DeleteWebhookMutation["deleteWebhook"]> {
    return this.run(OPERATIONS.DeleteWebhook, variables, options);
  }

  /**
   * Give a webhook a new signing secret. The old one stops working now. Needs webhooks:write.
   */
  rotateWebhookSecret(variables: T.RotateWebhookSecretMutationVariables, options?: CallOptions): Promise<T.RotateWebhookSecretMutation["rotateWebhookSecret"]> {
    return this.run(OPERATIONS.RotateWebhookSecret, variables, options);
  }

  /**
   * Send a "webhook.test" event now, and see how your URL answered. Needs webhooks:write.
   */
  sendTestWebhook(variables: T.SendTestWebhookMutationVariables, options?: CallOptions): Promise<T.SendTestWebhookMutation["sendTestWebhook"]> {
    return this.run(OPERATIONS.SendTestWebhook, variables, options);
  }

  /**
   * Send a delivery again, soon. Needs webhooks:write.
   */
  redeliverWebhook(variables: T.RedeliverWebhookMutationVariables, options?: CallOptions): Promise<T.RedeliverWebhookMutation["redeliverWebhook"]> {
    return this.run(OPERATIONS.RedeliverWebhook, variables, options);
  }

  /**
   * Send up to 100 workcenters. All or nothing.
   */
  upsertWorkcenters(variables: T.UpsertWorkcentersMutationVariables, options?: CallOptions): Promise<T.UpsertWorkcentersMutation["upsertWorkcenters"]> {
    return this.run(OPERATIONS.UpsertWorkcenters, variables, options);
  }

  /**
   * Send up to 100 stations. All or nothing. Send workcenters first.
   */
  upsertStations(variables: T.UpsertStationsMutationVariables, options?: CallOptions): Promise<T.UpsertStationsMutation["upsertStations"]> {
    return this.run(OPERATIONS.UpsertStations, variables, options);
  }

  /**
   * Send up to 100 customers. All or nothing.
   */
  upsertCustomers(variables: T.UpsertCustomersMutationVariables, options?: CallOptions): Promise<T.UpsertCustomersMutation["upsertCustomers"]> {
    return this.run(OPERATIONS.UpsertCustomers, variables, options);
  }

  /**
   * Send up to 100 materials. All or nothing: if one has a problem, none are saved.
   */
  upsertMaterials(variables: T.UpsertMaterialsMutationVariables, options?: CallOptions): Promise<T.UpsertMaterialsMutation["upsertMaterials"]> {
    return this.run(OPERATIONS.UpsertMaterials, variables, options);
  }

  /**
   * Send up to 100 products, with their bills of materials. All or nothing: if one has a problem, none are saved. Send materials first.
   */
  upsertProducts(variables: T.UpsertProductsMutationVariables, options?: CallOptions): Promise<T.UpsertProductsMutation["upsertProducts"]> {
    return this.run(OPERATIONS.UpsertProducts, variables, options);
  }

  /**
   * Send up to 100 tools, with their cavities. All or nothing.
   */
  upsertTools(variables: T.UpsertToolsMutationVariables, options?: CallOptions): Promise<T.UpsertToolsMutation["upsertTools"]> {
    return this.run(OPERATIONS.UpsertTools, variables, options);
  }

  /**
   * Send up to 100 jobs, with their tools and the products they make. All or nothing. Send tools and products first.
   */
  upsertJobs(variables: T.UpsertJobsMutationVariables, options?: CallOptions): Promise<T.UpsertJobsMutation["upsertJobs"]> {
    return this.run(OPERATIONS.UpsertJobs, variables, options);
  }

  /**
   * Send up to 100 runs to stations' lineups. A new run goes to the end of its station's queue; an update never moves it, because the plant can reorder runs. Changing a queued run's station or job takes it off and adds it again at the end. The lineup's rules are the same as in IMM: a running run can change its counts and dates only, and a closed one nothing. Safe to send again.
   */
  upsertProductionRuns(variables: T.UpsertProductionRunsMutationVariables, options?: CallOptions): Promise<T.UpsertProductionRunsMutation["upsertProductionRuns"]> {
    return this.run(OPERATIONS.UpsertProductionRuns, variables, options);
  }

  /**
   * Send one order, with its customer and lines. Safe to send again: the same order gives the same result.
   */
  upsertOrder(variables: T.UpsertOrderMutationVariables, options?: CallOptions): Promise<T.UpsertOrderMutation["upsertOrder"]> {
    return this.run(OPERATIONS.UpsertOrder, variables, options);
  }

  /**
   * Put runs in order at one station, by your ids. They take the places they already hold in its queue, in the order given, and every other run stays where it is. Only queued runs. Safe to send again.
   */
  sequenceLineup(variables: T.SequenceLineupMutationVariables, options?: CallOptions): Promise<T.SequenceLineupMutation["sequenceLineup"]> {
    return this.run(OPERATIONS.SequenceLineup, variables, options);
  }

  /**
   * Give up to 100 records made in IMM your own ids, by their id in IMM. From then on you can use your id wherever the API takes theirs, and renaming them in IMM changes nothing. An id another record already has is refused, not moved. All or nothing. Safe to send again.
   */
  linkExternalIds(variables: T.LinkExternalIdsMutationVariables, options?: CallOptions): Promise<T.LinkExternalIdsMutation["linkExternalIds"]> {
    return this.run(OPERATIONS.LinkExternalIds, variables, options);
  }

  /**
   * Make or change up to 100 custom entities and their fields, by key. A field can point at an entity sent in the same call. All or nothing.
   */
  upsertEntityModels(variables: T.UpsertEntityModelsMutationVariables, options?: CallOptions): Promise<T.UpsertEntityModelsMutation["upsertEntityModels"]> {
    return this.run(OPERATIONS.UpsertEntityModels, variables, options);
  }

  /**
   * Send up to 100 records of one custom entity. All or nothing.
   */
  upsertEntityRecords(variables: T.UpsertEntityRecordsMutationVariables, options?: CallOptions): Promise<T.UpsertEntityRecordsMutation["upsertEntityRecords"]> {
    return this.run(OPERATIONS.UpsertEntityRecords, variables, options);
  }
}
