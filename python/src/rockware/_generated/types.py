# Made by scripts/generate.py from the repo's schema/, operations/ and behavior.json. Don't edit it.
"""Every type the operations send and get back. Field names are the API's own."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, TypedDict

CycleMode = Literal["DISCRETE", "QUANTITY_PER_CYCLE", "QUANTITY_PER_INTERVAL"]
EntityFieldType = Literal["BOOLEAN", "DATE", "JSON", "NUMBER", "OBJECT", "SELECT", "TEXT", "TIMESTAMP"]
ExternalIdKind = Literal["CUSTOMER", "JOB", "STATION", "TOOL", "WORKCENTER"]
OrderStatus = Literal["CANCELLED", "COMPLETED", "OPEN"]
ProductionRunCloseReason = Literal["MET", "OVER", "SHORT", "SKIPPED"]
ProductionRunStatus = Literal["CLOSED", "QUEUED", "REMOVED", "RUNNING"]
RatePeriod = Literal["HOUR", "MINUTE", "SECOND"]
UpsertAction = Literal["CREATED", "UNCHANGED", "UPDATED"]
WebhookDeliveryStatus = Literal["FAILED", "PENDING", "RETRYING", "SUCCEEDED"]
WebhookEventType = Literal[
    "CUSTOMER_CREATED",
    "CUSTOMER_DELETED",
    "CUSTOMER_UPDATED",
    "JOB_CREATED",
    "JOB_DELETED",
    "JOB_UPDATED",
    "LINEUP_RUN_CREATED",
    "LINEUP_RUN_UPDATED",
    "MATERIAL_CREATED",
    "MATERIAL_DELETED",
    "MATERIAL_UPDATED",
    "ORDER_CREATED",
    "ORDER_DELETED",
    "ORDER_UPDATED",
    "PRODUCT_CREATED",
    "PRODUCT_DELETED",
    "PRODUCT_UPDATED",
]
WeightUnit = Literal["G", "KG", "LB", "OZ"]


class _BomLineInputRequired(TypedDict):
    material: str


class BomLineInput(_BomLineInputRequired, total=False):
    """One material a product uses."""

    itemCost: float | None
    weight: float | None
    weightUnits: WeightUnit | None


class _CustomerInputRequired(TypedDict):
    externalId: str
    name: str


class CustomerInput(_CustomerInputRequired, total=False):
    """Who the order is for. Found by externalId, never by name: made the first time, renamed if the name changes."""

    id: str | None


class _CustomerUpsertInputRequired(TypedDict):
    externalId: str


class CustomerUpsertInput(_CustomerUpsertInputRequired, total=False):
    """A customer. Fields left out are left as they are."""

    id: str | None
    name: str | None


class _EntityFieldInputRequired(TypedDict):
    key: str


class EntityFieldInput(_EntityFieldInputRequired, total=False):
    """A field, found by its key. Fields left out are left as they are."""

    description: str | None
    isList: bool | None
    label: str | None
    options: list[EntityFieldOptionInput] | None
    refModel: str | None
    required: bool | None
    sortOrder: int | None
    type: EntityFieldType | None


class _EntityFieldOptionInputRequired(TypedDict):
    value: str


class EntityFieldOptionInput(_EntityFieldOptionInputRequired, total=False):
    label: str | None


class _EntityModelInputRequired(TypedDict):
    key: str


class EntityModelInput(_EntityModelInputRequired, total=False):
    """A custom entity, found by its key. Fields left out are left as they are."""

    description: str | None
    fields: list[EntityFieldInput] | None
    label: str | None


class _EntityRecordInputRequired(TypedDict):
    externalId: str


class EntityRecordInput(_EntityRecordInputRequired, total=False):
    """A custom entity record. Fields left out are left as they are."""

    id: str | None
    name: str | None
    values: Any | None


class _ExternalIdLinkInputRequired(TypedDict):
    externalId: str
    id: str


class ExternalIdLinkInput(_ExternalIdLinkInputRequired, total=False):
    remove: bool | None


class _JobInputRequired(TypedDict):
    externalId: str


class JobInput(_JobInputRequired, total=False):
    """A job. Fields left out are left as they are; null clears one that can be empty."""

    description: str | None
    id: str | None
    items: list[JobItemInput] | None
    name: str | None
    productsPerCycle: int | None
    profileId: str | None
    standardCycle: float | None
    standardQuantity: float | None
    standardRate: float | None
    standardRatePeriod: RatePeriod | None
    standardRateUnit: str | None
    tools: list[str] | None


class _JobItemInputRequired(TypedDict):
    product: str


class JobItemInput(_JobItemInputRequired, total=False):
    """A product the job makes. Found by product, tool and cavity together."""

    cavity: str | None
    quantity: int | None
    tool: str | None


class _MaterialInputRequired(TypedDict):
    externalId: str


class MaterialInput(_MaterialInputRequired, total=False):
    """A material. Fields left out are left as they are."""

    description: str | None
    externalNumber: str | None
    materialNumber: str | None
    name: str | None
    shortCode: str | None
    unitCost: float | None
    weightUnits: WeightUnit | None


class _OrderInputRequired(TypedDict):
    externalId: str


class OrderInput(_OrderInputRequired, total=False):
    """An order. Fields left out are left as they are; null clears one that can be empty."""

    cancel: bool | None
    customer: CustomerInput | None
    defaultTargetQuantity: float | None
    dueDate: str | datetime | None
    lines: list[OrderLineInput] | None
    notes: str | None
    orderNumber: str | None
    poNumber: str | None
    startDate: str | datetime | None


class _OrderLineInputRequired(TypedDict):
    product: str
    targetQuantity: float


class OrderLineInput(_OrderLineInputRequired, total=False):
    pass


class _ProductInputRequired(TypedDict):
    externalId: str


class ProductInput(_ProductInputRequired, total=False):
    """A product. Fields left out are left as they are."""

    description: str | None
    externalSku: str | None
    itemCost: float | None
    materials: list[BomLineInput] | None
    name: str | None
    sku: str | None
    weight: float | None
    weightUnits: WeightUnit | None


class _ProductionRunInputRequired(TypedDict):
    externalId: str


class ProductionRunInput(_ProductionRunInputRequired, total=False):
    """A run: one job at one station, such as one of your work orders. Fields left out are left as they are; null clears startBy or endBy."""

    cancel: bool | None
    endBy: str | datetime | None
    job: str | None
    parts: list[ProductionRunPartInput] | None
    quantity: float | None
    startBy: str | datetime | None
    station: str | None


class _ProductionRunPartInputRequired(TypedDict):
    product: str
    requiredGood: float


class ProductionRunPartInput(_ProductionRunPartInputRequired, total=False):
    pass


class _StationInputRequired(TypedDict):
    externalId: str


class StationInput(_StationInputRequired, total=False):
    """A station: one machine or work spot. Fields left out are left as they are; null clears one that can be empty. A station that follows a profile gets how it counts from the profile; only its speed can be set here."""

    cycleMode: CycleMode | None
    description: str | None
    downtimeDetect: float | None
    fastDetect: float | None
    id: str | None
    name: str | None
    profileId: str | None
    quantityUnit: str | None
    slowDetect: float | None
    sortOrder: int | None
    standardCycle: float | None
    standardQuantity: float | None
    standardRate: float | None
    standardRatePeriod: RatePeriod | None
    standardRateUnit: str | None
    useProfileSpeed: bool | None
    variationId: str | None
    workcenter: str | None


class _ToolCavityInputRequired(TypedDict):
    name: str


class ToolCavityInput(_ToolCavityInputRequired, total=False):
    """A cavity, found by its name on the tool."""

    position: int | None


class _ToolInputRequired(TypedDict):
    externalId: str


class ToolInput(_ToolInputRequired, total=False):
    """A tool. Fields left out are left as they are; null clears one that can be empty."""

    cavities: list[ToolCavityInput] | None
    cavityCount: int | None
    description: str | None
    id: str | None
    name: str | None


class _WebhookInputRequired(TypedDict):
    events: list[WebhookEventType]
    url: str


class WebhookInput(_WebhookInputRequired, total=False):
    enabled: bool | None


class WebhookUpdateInput(TypedDict, total=False):
    """Only the fields you send change. events is the whole new list."""

    enabled: bool | None
    events: list[WebhookEventType] | None
    url: str | None


class _WorkcenterInputRequired(TypedDict):
    externalId: str


class WorkcenterInput(_WorkcenterInputRequired, total=False):
    """A workcenter: a group of stations. Fields left out are left as they are."""

    description: str | None
    downtimeDetect: float | None
    fastDetect: float | None
    id: str | None
    name: str | None
    slowDetect: float | None


class ExternalIdFields(TypedDict):
    id: str
    source: str


class SiteFields(TypedDict):
    id: str
    name: str
    description: str | None
    timezone: str
    updatedAt: str


class WorkcenterFields(TypedDict):
    id: str
    name: str
    description: str | None
    parentId: str | None
    externalIds: list[ExternalIdFields]
    createdAt: str
    updatedAt: str


class StationFieldsWorkcenter(TypedDict):
    id: str
    name: str


class StationFieldsCurrentJob(TypedDict):
    id: str
    name: str | None


class StationFields(TypedDict):
    id: str
    name: str
    description: str | None
    sortOrder: int
    workcenterId: str | None
    workcenter: StationFieldsWorkcenter | None
    currentJobId: str | None
    currentJob: StationFieldsCurrentJob | None
    externalIds: list[ExternalIdFields]
    archivedAt: str | None
    createdAt: str
    updatedAt: str
    deletedAt: str | None


class CustomerFields(TypedDict):
    id: str
    name: str
    externalIds: list[ExternalIdFields]
    createdAt: str
    updatedAt: str
    deletedAt: str | None


class MaterialFields(TypedDict):
    id: str
    materialNumber: str | None
    name: str | None
    description: str | None
    classification: str | None
    shortCode: str | None
    externalNumber: str | None
    unitCost: str | None
    version: int | None
    externalIds: list[ExternalIdFields]
    archivedAt: str | None
    createdAt: str
    updatedAt: str
    deletedAt: str | None


class ProductFields(TypedDict):
    id: str
    sku: str | None
    name: str | None
    description: str | None
    externalSku: str | None
    itemCost: str | None
    weight: str | None
    version: int | None
    externalIds: list[ExternalIdFields]
    archivedAt: str | None
    createdAt: str
    updatedAt: str
    deletedAt: str | None


class ToolFieldsCavities(TypedDict):
    id: str
    name: str | None
    position: int | None


class ToolFields(TypedDict):
    id: str
    name: str | None
    description: str | None
    cavityCount: int | None
    cavities: list[ToolFieldsCavities]
    version: int | None
    externalIds: list[ExternalIdFields]
    archivedAt: str | None
    createdAt: str
    updatedAt: str
    deletedAt: str | None


class JobFieldsTools(TypedDict):
    id: str
    name: str | None


class JobFieldsItemsProduct(TypedDict):
    id: str
    sku: str | None


class JobFieldsItemsTool(TypedDict):
    id: str
    name: str | None


class JobFieldsItems(TypedDict):
    id: str
    quantity: int
    isActive: bool
    cavityId: str | None
    product: JobFieldsItemsProduct | None
    tool: JobFieldsItemsTool | None


class JobFieldsEligibleStations(TypedDict):
    id: str
    name: str


class JobFields(TypedDict):
    id: str
    name: str | None
    description: str | None
    version: int | None
    standardRate: str | None
    standardRateUnit: str | None
    standardRatePeriod: RatePeriod | None
    standardCycle: str | None
    standardQuantity: str | None
    productsPerCycle: int | None
    profileId: str | None
    tools: list[JobFieldsTools]
    items: list[JobFieldsItems]
    eligibleStations: list[JobFieldsEligibleStations]
    externalIds: list[ExternalIdFields]
    archivedAt: str | None
    createdAt: str
    updatedAt: str
    deletedAt: str | None


class OrderFieldsCustomer(TypedDict):
    id: str
    name: str


class OrderFieldsLinesProduct(TypedDict):
    id: str
    sku: str | None


class OrderFieldsLines(TypedDict):
    id: str
    productId: str
    product: OrderFieldsLinesProduct | None
    targetQuantity: str


class OrderFields(TypedDict):
    id: str
    orderNumber: str
    poNumber: str | None
    status: OrderStatus
    notes: str | None
    customerId: str | None
    customer: OrderFieldsCustomer | None
    defaultTargetQuantity: str
    startDate: str | None
    dueDate: str | None
    openedAt: str | None
    completedAt: str | None
    cancelledAt: str | None
    lines: list[OrderFieldsLines]
    externalIds: list[ExternalIdFields]
    createdAt: str
    updatedAt: str
    deletedAt: str | None


class ProductionRunFieldsStation(TypedDict):
    id: str
    name: str


class ProductionRunFieldsJob(TypedDict):
    id: str
    name: str | None


class ProductionRunFieldsPartsProduct(TypedDict):
    id: str
    sku: str | None


class ProductionRunFieldsParts(TypedDict):
    productId: str
    product: ProductionRunFieldsPartsProduct | None
    perCycle: int
    requiredGood: str
    goodCount: str | None
    scrapCount: str | None
    metAt: str | None


class ProductionRunFields(TypedDict):
    id: str
    status: ProductionRunStatus
    rank: int
    stationId: str
    station: ProductionRunFieldsStation | None
    workcenterId: str
    jobId: str
    job: ProductionRunFieldsJob | None
    parts: list[ProductionRunFieldsParts]
    startBy: str | None
    endBy: str | None
    startByMissed: bool
    endByMissed: bool
    plannedStart: str | None
    plannedEnd: str | None
    plannedBusinessDate: str | None
    plannedShiftName: str | None
    plannedChangeoverMinutes: int | None
    actualChangeoverMinutes: int | None
    runStartedAt: str | None
    quantityMetAt: str | None
    closedAt: str | None
    closedBusinessDate: str | None
    closeReason: ProductionRunCloseReason | None
    skipCount: int
    jobChangedAt: str | None
    externalIds: list[ExternalIdFields]
    createdAt: str
    updatedAt: str


class EntityModelFieldsFieldsOptions(TypedDict):
    value: str
    label: str | None


class EntityModelFieldsFields(TypedDict):
    key: str
    label: str
    description: str | None
    type: EntityFieldType
    required: bool
    isList: bool
    refModel: str | None
    options: list[EntityModelFieldsFieldsOptions] | None


class EntityModelFields(TypedDict):
    id: str
    key: str
    label: str
    description: str | None
    version: int
    fields: list[EntityModelFieldsFields]
    createdAt: str
    updatedAt: str


class EntityRecordFields(TypedDict):
    id: str
    model: str
    name: str
    values: Any
    deleted: bool
    externalIds: list[ExternalIdFields]
    createdAt: str
    updatedAt: str


class WebhookFields(TypedDict):
    id: str
    url: str
    events: list[WebhookEventType]
    enabled: bool
    createdAt: str
    updatedAt: str


class WebhookDeliveryFields(TypedDict):
    id: str
    eventId: str | None
    type: str | None
    status: WebhookDeliveryStatus
    attempts: int
    responseStatus: int | None
    error: str | None
    startedAt: str
    finishedAt: str | None
    nextAttemptAt: str | None


class UpsertErrorFields(TypedDict):
    code: str
    field: str | None
    message: str


class ListWorkcentersResultPageInfo(TypedDict):
    hasNextPage: bool
    endCursor: str | None


class ListWorkcentersResult(TypedDict):
    nodes: list[WorkcenterFields]
    pageInfo: ListWorkcentersResultPageInfo


class ListStationsResultPageInfo(TypedDict):
    hasNextPage: bool
    endCursor: str | None


class ListStationsResult(TypedDict):
    nodes: list[StationFields]
    pageInfo: ListStationsResultPageInfo


class ListCustomersResultPageInfo(TypedDict):
    hasNextPage: bool
    endCursor: str | None


class ListCustomersResult(TypedDict):
    nodes: list[CustomerFields]
    pageInfo: ListCustomersResultPageInfo


class ListMaterialsResultPageInfo(TypedDict):
    hasNextPage: bool
    endCursor: str | None


class ListMaterialsResult(TypedDict):
    nodes: list[MaterialFields]
    pageInfo: ListMaterialsResultPageInfo


class ListProductsResultPageInfo(TypedDict):
    hasNextPage: bool
    endCursor: str | None


class ListProductsResult(TypedDict):
    nodes: list[ProductFields]
    pageInfo: ListProductsResultPageInfo


class ListToolsResultPageInfo(TypedDict):
    hasNextPage: bool
    endCursor: str | None


class ListToolsResult(TypedDict):
    nodes: list[ToolFields]
    pageInfo: ListToolsResultPageInfo


class ListJobsResultPageInfo(TypedDict):
    hasNextPage: bool
    endCursor: str | None


class ListJobsResult(TypedDict):
    nodes: list[JobFields]
    pageInfo: ListJobsResultPageInfo


class ListOrdersResultPageInfo(TypedDict):
    hasNextPage: bool
    endCursor: str | None


class ListOrdersResult(TypedDict):
    nodes: list[OrderFields]
    pageInfo: ListOrdersResultPageInfo


class ListProductionRunsResultPageInfo(TypedDict):
    hasNextPage: bool
    endCursor: str | None


class ListProductionRunsResult(TypedDict):
    nodes: list[ProductionRunFields]
    pageInfo: ListProductionRunsResultPageInfo


class GetStationLineupResultLineupProgress(TypedDict):
    productId: str
    requiredGood: str
    good: float
    scrap: float


class GetStationLineupResultLineup(TypedDict):
    position: int
    predictedChangeoverStart: str
    predictedStart: str
    predictedEnd: str
    startByAtRisk: bool
    endByAtRisk: bool
    progress: list[GetStationLineupResultLineupProgress]
    run: ProductionRunFields


class GetStationLineupResult(TypedDict):
    id: str
    name: str
    lineup: list[GetStationLineupResultLineup] | None


class ListEntityRecordsResultPageInfo(TypedDict):
    hasNextPage: bool
    endCursor: str | None


class ListEntityRecordsResult(TypedDict):
    nodes: list[EntityRecordFields]
    pageInfo: ListEntityRecordsResultPageInfo


class CreateWebhookResult(TypedDict):
    secret: str
    webhook: WebhookFields


class RotateWebhookSecretResult(TypedDict):
    secret: str
    webhook: WebhookFields


class UpsertWorkcentersResultResults(TypedDict):
    externalId: str
    action: UpsertAction
    workcenter: WorkcenterFields | None


class UpsertWorkcentersResult(TypedDict):
    results: list[UpsertWorkcentersResultResults]
    errors: list[UpsertErrorFields]


class UpsertStationsResultResults(TypedDict):
    externalId: str
    action: UpsertAction
    station: StationFields | None


class UpsertStationsResult(TypedDict):
    results: list[UpsertStationsResultResults]
    errors: list[UpsertErrorFields]


class UpsertCustomersResultResults(TypedDict):
    externalId: str
    action: UpsertAction
    customer: CustomerFields | None


class UpsertCustomersResult(TypedDict):
    results: list[UpsertCustomersResultResults]
    errors: list[UpsertErrorFields]


class UpsertMaterialsResultResults(TypedDict):
    externalId: str
    action: UpsertAction
    material: MaterialFields | None


class UpsertMaterialsResult(TypedDict):
    results: list[UpsertMaterialsResultResults]
    errors: list[UpsertErrorFields]


class UpsertProductsResultResults(TypedDict):
    externalId: str
    action: UpsertAction
    product: ProductFields | None


class UpsertProductsResult(TypedDict):
    results: list[UpsertProductsResultResults]
    errors: list[UpsertErrorFields]


class UpsertToolsResultResults(TypedDict):
    externalId: str
    action: UpsertAction
    tool: ToolFields | None


class UpsertToolsResult(TypedDict):
    results: list[UpsertToolsResultResults]
    errors: list[UpsertErrorFields]


class UpsertJobsResultResults(TypedDict):
    externalId: str
    action: UpsertAction
    job: JobFields | None


class UpsertJobsResult(TypedDict):
    results: list[UpsertJobsResultResults]
    errors: list[UpsertErrorFields]


class UpsertProductionRunsResultResults(TypedDict):
    externalId: str
    action: UpsertAction
    run: ProductionRunFields | None


class UpsertProductionRunsResult(TypedDict):
    results: list[UpsertProductionRunsResultResults]
    errors: list[UpsertErrorFields]


class UpsertOrderResult(TypedDict):
    action: UpsertAction | None
    order: OrderFields | None
    errors: list[UpsertErrorFields]


class SequenceLineupResultStation(TypedDict):
    id: str
    name: str


class SequenceLineupResult(TypedDict):
    action: UpsertAction | None
    station: SequenceLineupResultStation | None
    errors: list[UpsertErrorFields]


class LinkExternalIdsResultResults(TypedDict):
    id: str
    externalId: str
    action: UpsertAction


class LinkExternalIdsResult(TypedDict):
    results: list[LinkExternalIdsResultResults]
    errors: list[UpsertErrorFields]


class UpsertEntityModelsResultResults(TypedDict):
    key: str
    action: UpsertAction
    model: EntityModelFields | None


class UpsertEntityModelsResult(TypedDict):
    results: list[UpsertEntityModelsResultResults]
    errors: list[UpsertErrorFields]


class UpsertEntityRecordsResultResults(TypedDict):
    externalId: str
    action: UpsertAction
    record: EntityRecordFields | None


class UpsertEntityRecordsResult(TypedDict):
    results: list[UpsertEntityRecordsResultResults]
    errors: list[UpsertErrorFields]
