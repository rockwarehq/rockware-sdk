// Made by scripts/generate.ts from the repo's schema/, operations/ and behavior.json. Don't edit it.
/* eslint-disable */
export type Maybe<T> = T | null;
export type InputMaybe<T> = T | null | undefined;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  /** A point in time, as an ISO 8601 string with a time zone (e.g. 2026-11-02T14:30:00.000Z). */
  DateTime: { input: string; output: string; }
  /** An exact decimal number, as a string (e.g. "12.5000"), so no precision is lost. */
  Decimal: { input: string; output: string; }
  /** Any JSON value: an object, a list, a string, a number, true, false or null. */
  JSON: { input: unknown; output: unknown; }
};

/** One material a product uses. */
export type BomLineInput = {
  itemCost?: InputMaybe<Scalars['Float']['input']>;
  /** The material's externalId (sent before, or in the same call), or its material number. */
  material: Scalars['String']['input'];
  /** How much of it one part uses. */
  weight?: InputMaybe<Scalars['Float']['input']>;
  weightUnits?: InputMaybe<WeightUnit>;
};

/** Who the order is for. Found by externalId, never by name: made the first time, renamed if the name changes. */
export type CustomerInput = {
  /** Its id in your system. */
  externalId: Scalars['String']['input'];
  /** Its id in IMM, to give a customer made in IMM this externalId. Only needed the first time; without it a new externalId makes a new customer, and a taken name is refused (DUPLICATE_NAME). */
  id?: InputMaybe<Scalars['ID']['input']>;
  name: Scalars['String']['input'];
};

/** A customer. Fields left out are left as they are. */
export type CustomerUpsertInput = {
  /** Its id in your system. */
  externalId: Scalars['String']['input'];
  /** Its id in IMM, to give a record made in IMM this externalId. Only needed the first time; without it a new externalId makes a new record. */
  id?: InputMaybe<Scalars['ID']['input']>;
  /** Needed to make a new customer. Unique at the plant. */
  name?: InputMaybe<Scalars['String']['input']>;
};

/** How a station counts: a part per cycle, a quantity per cycle, or a quantity per time. */
export type CycleMode =
  | 'DISCRETE'
  | 'QUANTITY_PER_CYCLE'
  | 'QUANTITY_PER_INTERVAL';

/** A field, found by its key. Fields left out are left as they are. */
export type EntityFieldInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  isList?: InputMaybe<Scalars['Boolean']['input']>;
  /** Its key in a record's values, e.g. cavity_count. */
  key: Scalars['String']['input'];
  /** Needed for a new field. */
  label?: InputMaybe<Scalars['String']['input']>;
  /** For a SELECT field: its choices. */
  options?: InputMaybe<Array<EntityFieldOptionInput>>;
  /** For an OBJECT field: the key of the entity it points at. */
  refModel?: InputMaybe<Scalars['String']['input']>;
  required?: InputMaybe<Scalars['Boolean']['input']>;
  sortOrder?: InputMaybe<Scalars['Int']['input']>;
  /** Needed for a new field. */
  type?: InputMaybe<EntityFieldType>;
};

export type EntityFieldOptionInput = {
  label?: InputMaybe<Scalars['String']['input']>;
  value: Scalars['String']['input'];
};

/** What a custom field holds. */
export type EntityFieldType =
  /** true or false. */
  | 'BOOLEAN'
  /** A date, as a string (e.g. 2026-11-12). */
  | 'DATE'
  /** Any JSON. */
  | 'JSON'
  /** A number. */
  | 'NUMBER'
  /** A record of another entity (refModel), by its id. */
  | 'OBJECT'
  /** One of the field's options, by value. */
  | 'SELECT'
  /** A string. */
  | 'TEXT'
  /** A point in time, as an ISO 8601 string. */
  | 'TIMESTAMP';

/** A custom entity, found by its key. Fields left out are left as they are. */
export type EntityModelInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  /** Fields to add or change. Fields not listed are left as they are. */
  fields?: InputMaybe<Array<EntityFieldInput>>;
  /** Its key, e.g. mold. */
  key: Scalars['String']['input'];
  /** Needed for a new entity. */
  label?: InputMaybe<Scalars['String']['input']>;
};

/** A custom entity record. Fields left out are left as they are. */
export type EntityRecordInput = {
  /** Its id in your system. */
  externalId: Scalars['String']['input'];
  /** Its id in IMM, to give a record made in IMM this externalId. Only needed the first time; without it a new externalId makes a new record. */
  id?: InputMaybe<Scalars['ID']['input']>;
  /** Its name. Left out, a new record gets one like "Mold 3". */
  name?: InputMaybe<Scalars['String']['input']>;
  /** Values by field key: fields left out stay as they are; null clears one. An OBJECT field takes a record's id, or { "externalId": "…" } for one you sent from the same source. */
  values?: InputMaybe<Scalars['JSON']['input']>;
};

/** Records made in IMM that you can link your ids to. */
export type ExternalIdKind =
  | 'CUSTOMER'
  | 'JOB'
  | 'STATION'
  | 'TOOL'
  | 'WORKCENTER';

export type ExternalIdLinkInput = {
  /** Its id in your system. */
  externalId: Scalars['String']['input'];
  /** The record's id in IMM. */
  id: Scalars['ID']['input'];
  /** true takes this link off instead. */
  remove?: InputMaybe<Scalars['Boolean']['input']>;
};

/** A job. Fields left out are left as they are; null clears one that can be empty. */
export type JobInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  /** Its id in your system. */
  externalId: Scalars['String']['input'];
  /** Its id in IMM, to give a record made in IMM this externalId. Only needed the first time; without it a new externalId makes a new record. */
  id?: InputMaybe<Scalars['ID']['input']>;
  /** Listed items are added or updated; ones not listed are left alone. */
  items?: InputMaybe<Array<JobItemInput>>;
  /** Needed to make a new job. */
  name?: InputMaybe<Scalars['String']['input']>;
  productsPerCycle?: InputMaybe<Scalars['Int']['input']>;
  /** The station profile (kind of machine) the job is made for. */
  profileId?: InputMaybe<Scalars['ID']['input']>;
  /** Seconds per cycle. */
  standardCycle?: InputMaybe<Scalars['Float']['input']>;
  standardQuantity?: InputMaybe<Scalars['Float']['input']>;
  standardRate?: InputMaybe<Scalars['Float']['input']>;
  standardRatePeriod?: InputMaybe<RatePeriod>;
  standardRateUnit?: InputMaybe<Scalars['String']['input']>;
  /** Tools to put on the job, by externalId or IMM id. Tools not listed stay on. */
  tools?: InputMaybe<Array<Scalars['String']['input']>>;
};

/** A product the job makes. Found by product, tool and cavity together. */
export type JobItemInput = {
  /** A cavity's name on that tool. */
  cavity?: InputMaybe<Scalars['String']['input']>;
  /** The product's externalId, its IMM id, or its SKU. */
  product: Scalars['String']['input'];
  /** How many one cycle makes. Defaults to 1 for a new item. */
  quantity?: InputMaybe<Scalars['Int']['input']>;
  /** The tool it comes from: its externalId or IMM id. The tool must be on the job. */
  tool?: InputMaybe<Scalars['String']['input']>;
};

/** A material. Fields left out are left as they are. */
export type MaterialInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  /** Its id in your system. */
  externalId: Scalars['String']['input'];
  externalNumber?: InputMaybe<Scalars['String']['input']>;
  /** The plant's material number. Defaults to externalId. A new externalId matches a material with this number. */
  materialNumber?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  shortCode?: InputMaybe<Scalars['String']['input']>;
  unitCost?: InputMaybe<Scalars['Float']['input']>;
  /** The unit it is stocked in. */
  weightUnits?: InputMaybe<WeightUnit>;
};

/** An order. Fields left out are left as they are; null clears one that can be empty. */
export type OrderInput = {
  /** true cancels the order. A cancelled order can't be opened again. Completing happens in the plant. */
  cancel?: InputMaybe<Scalars['Boolean']['input']>;
  /** null takes the customer off the order. */
  customer?: InputMaybe<CustomerInput>;
  defaultTargetQuantity?: InputMaybe<Scalars['Float']['input']>;
  dueDate?: InputMaybe<Scalars['DateTime']['input']>;
  /** Its id in your system. */
  externalId: Scalars['String']['input'];
  /** Every line the order should have. Lines not listed are removed. Leave it out to keep the lines. */
  lines?: InputMaybe<Array<OrderLineInput>>;
  notes?: InputMaybe<Scalars['String']['input']>;
  /** The plant's order number. Defaults to externalId. A new externalId matches an order with this number. */
  orderNumber?: InputMaybe<Scalars['String']['input']>;
  poNumber?: InputMaybe<Scalars['String']['input']>;
  startDate?: InputMaybe<Scalars['DateTime']['input']>;
};

export type OrderLineInput = {
  /** The product's externalId, or its SKU. */
  product: Scalars['String']['input'];
  /** How many to make. */
  targetQuantity: Scalars['Float']['input'];
};

export type OrderStatus =
  | 'CANCELLED'
  | 'COMPLETED'
  | 'OPEN';

/** A product. Fields left out are left as they are. */
export type ProductInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  /** Its id in your system. */
  externalId: Scalars['String']['input'];
  externalSku?: InputMaybe<Scalars['String']['input']>;
  itemCost?: InputMaybe<Scalars['Float']['input']>;
  /** Its bill of materials. Listed materials are added or updated; ones not listed are left alone. */
  materials?: InputMaybe<Array<BomLineInput>>;
  name?: InputMaybe<Scalars['String']['input']>;
  /** The plant's SKU. Defaults to externalId. A new externalId matches a product with this SKU. */
  sku?: InputMaybe<Scalars['String']['input']>;
  /** Part weight. */
  weight?: InputMaybe<Scalars['Float']['input']>;
  weightUnits?: InputMaybe<WeightUnit>;
};

/** How a run closed. */
export type ProductionRunCloseReason =
  /** Every part met its count. */
  | 'MET'
  /** Every part met its count, and at least one went over the tolerance. */
  | 'OVER'
  /** The job changed before every part met its count. */
  | 'SHORT'
  /** Skipped and closed without running: a missed plan. */
  | 'SKIPPED';

/** A run: one job at one station, such as one of your work orders. Fields left out are left as they are; null clears startBy or endBy. */
export type ProductionRunInput = {
  /** true takes a queued run off the lineup. A running run is ended in the plant. */
  cancel?: InputMaybe<Scalars['Boolean']['input']>;
  /** Should end by. Raises an alert in the plant when at risk. */
  endBy?: InputMaybe<Scalars['DateTime']['input']>;
  /** Its id in your system, such as your work order id. */
  externalId: Scalars['String']['input'];
  /** The job's externalId, or its id. Needed for a new run. */
  job?: InputMaybe<Scalars['String']['input']>;
  /** Good ones needed, per part. Wins over quantity for the parts it names. */
  parts?: InputMaybe<Array<ProductionRunPartInput>>;
  /** Good ones needed, for every part the job makes. */
  quantity?: InputMaybe<Scalars['Float']['input']>;
  /** Should start by. Raises an alert in the plant when at risk. */
  startBy?: InputMaybe<Scalars['DateTime']['input']>;
  /** The station's externalId, or its id. Needed for a new run. */
  station?: InputMaybe<Scalars['String']['input']>;
};

export type ProductionRunPartInput = {
  /** The product's externalId, its id, or its SKU. The run's job must make it. */
  product: Scalars['String']['input'];
  /** Good ones needed. */
  requiredGood: Scalars['Float']['input'];
};

/** Where a run is in its life. CLOSED and REMOVED are final. */
export type ProductionRunStatus =
  /** Rolled off when the station changed to another job, or skipped. See closeReason. */
  | 'CLOSED'
  /** Waiting its turn at the station. */
  | 'QUEUED'
  /** Taken off the lineup before it ran. */
  | 'REMOVED'
  /** The station changed to its job; it's counting toward it. */
  | 'RUNNING';

export type RatePeriod =
  | 'HOUR'
  | 'MINUTE'
  | 'SECOND';

/** A station: one machine or work spot. Fields left out are left as they are; null clears one that can be empty. A station that follows a profile gets how it counts from the profile; only its speed can be set here. */
export type StationInput = {
  cycleMode?: InputMaybe<CycleMode>;
  description?: InputMaybe<Scalars['String']['input']>;
  /** Seconds of no cycles before it counts as down (downtimeDetect), or the share of standard speed below which it's slow (slowDetect) and above which it's fast (fastDetect). null uses its workcenter's; 0 turns it off. */
  downtimeDetect?: InputMaybe<Scalars['Float']['input']>;
  /** Its id in your system. */
  externalId: Scalars['String']['input'];
  fastDetect?: InputMaybe<Scalars['Float']['input']>;
  /** Its id in IMM, to give a record made in IMM this externalId. Only needed the first time; without it a new externalId makes a new record. */
  id?: InputMaybe<Scalars['ID']['input']>;
  /** Needed to make a new station. Unique at the plant. */
  name?: InputMaybe<Scalars['String']['input']>;
  /** Follow this station profile. null stops following; the values stay. */
  profileId?: InputMaybe<Scalars['ID']['input']>;
  quantityUnit?: InputMaybe<Scalars['String']['input']>;
  slowDetect?: InputMaybe<Scalars['Float']['input']>;
  sortOrder?: InputMaybe<Scalars['Int']['input']>;
  /** Seconds per cycle. */
  standardCycle?: InputMaybe<Scalars['Float']['input']>;
  standardQuantity?: InputMaybe<Scalars['Float']['input']>;
  standardRate?: InputMaybe<Scalars['Float']['input']>;
  standardRatePeriod?: InputMaybe<RatePeriod>;
  standardRateUnit?: InputMaybe<Scalars['String']['input']>;
  /** Use the profile's usual speed instead of its own. */
  useProfileSpeed?: InputMaybe<Scalars['Boolean']['input']>;
  /** Which of the profile's variations. */
  variationId?: InputMaybe<Scalars['ID']['input']>;
  /** Its workcenter: the workcenter's externalId or IMM id. null takes it out of its workcenter. */
  workcenter?: InputMaybe<Scalars['String']['input']>;
};

/** A cavity, found by its name on the tool. */
export type ToolCavityInput = {
  name: Scalars['String']['input'];
  position?: InputMaybe<Scalars['Int']['input']>;
};

/** A tool. Fields left out are left as they are; null clears one that can be empty. */
export type ToolInput = {
  /** Listed cavities are added or updated; ones not listed are left alone. */
  cavities?: InputMaybe<Array<ToolCavityInput>>;
  cavityCount?: InputMaybe<Scalars['Int']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  /** Its id in your system. */
  externalId: Scalars['String']['input'];
  /** Its id in IMM, to give a record made in IMM this externalId. Only needed the first time; without it a new externalId makes a new record. */
  id?: InputMaybe<Scalars['ID']['input']>;
  /** Needed to make a new tool. */
  name?: InputMaybe<Scalars['String']['input']>;
};

/** What a write did. */
export type UpsertAction =
  /** A new record was made. */
  | 'CREATED'
  /** The record already matched; nothing was saved. */
  | 'UNCHANGED'
  /** The record was changed. */
  | 'UPDATED';

export type WebhookDeliveryStatus =
  /** It failed, and won't be sent again unless you redeliver it. */
  | 'FAILED'
  /** Being sent now. */
  | 'PENDING'
  /** It failed, and will be sent again at nextAttemptAt. */
  | 'RETRYING'
  /** Your URL answered 2xx. */
  | 'SUCCEEDED';

/** A kind of record change a webhook can follow. ORDER_UPDATED is sent as type "order.updated", and so on. */
export type WebhookEventType =
  | 'CUSTOMER_CREATED'
  | 'CUSTOMER_DELETED'
  | 'CUSTOMER_UPDATED'
  | 'JOB_CREATED'
  | 'JOB_DELETED'
  | 'JOB_UPDATED'
  | 'LINEUP_RUN_CREATED'
  | 'LINEUP_RUN_UPDATED'
  | 'MATERIAL_CREATED'
  | 'MATERIAL_DELETED'
  | 'MATERIAL_UPDATED'
  | 'ORDER_CREATED'
  | 'ORDER_DELETED'
  | 'ORDER_UPDATED'
  | 'PRODUCT_CREATED'
  | 'PRODUCT_DELETED'
  | 'PRODUCT_UPDATED';

export type WebhookInput = {
  enabled?: InputMaybe<Scalars['Boolean']['input']>;
  events: Array<WebhookEventType>;
  /** An https URL on the public internet. */
  url: Scalars['String']['input'];
};

/** Only the fields you send change. events is the whole new list. */
export type WebhookUpdateInput = {
  enabled?: InputMaybe<Scalars['Boolean']['input']>;
  events?: InputMaybe<Array<WebhookEventType>>;
  url?: InputMaybe<Scalars['String']['input']>;
};

export type WeightUnit =
  | 'G'
  | 'KG'
  | 'LB'
  | 'OZ';

/** A workcenter: a group of stations. Fields left out are left as they are. */
export type WorkcenterInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  /** Seconds of no cycles before it counts as down (downtimeDetect), or the share of standard speed below which it's slow (slowDetect) and above which it's fast (fastDetect). */
  downtimeDetect?: InputMaybe<Scalars['Float']['input']>;
  /** Its id in your system. */
  externalId: Scalars['String']['input'];
  fastDetect?: InputMaybe<Scalars['Float']['input']>;
  /** Its id in IMM, to give a record made in IMM this externalId. Only needed the first time; without it a new externalId makes a new record. */
  id?: InputMaybe<Scalars['ID']['input']>;
  /** Needed to make a new workcenter. */
  name?: InputMaybe<Scalars['String']['input']>;
  slowDetect?: InputMaybe<Scalars['Float']['input']>;
};

export type ExternalIdFieldsFragment = { id: string, source: string };

export type SiteFieldsFragment = { id: string, name: string, description?: string | null, timezone: string, updatedAt: string };

export type WorkcenterFieldsFragment = { id: string, name: string, description?: string | null, parentId?: string | null, createdAt: string, updatedAt: string, externalIds: Array<{ id: string, source: string }> };

export type StationFieldsFragment = { id: string, name: string, description?: string | null, sortOrder: number, workcenterId?: string | null, currentJobId?: string | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, workcenter?: { id: string, name: string } | null, currentJob?: { id: string, name?: string | null } | null, externalIds: Array<{ id: string, source: string }> };

export type CustomerFieldsFragment = { id: string, name: string, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> };

export type MaterialFieldsFragment = { id: string, materialNumber?: string | null, name?: string | null, description?: string | null, classification?: string | null, shortCode?: string | null, externalNumber?: string | null, unitCost?: string | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> };

export type ProductFieldsFragment = { id: string, sku?: string | null, name?: string | null, description?: string | null, externalSku?: string | null, itemCost?: string | null, weight?: string | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> };

export type ToolFieldsFragment = { id: string, name?: string | null, description?: string | null, cavityCount?: number | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, cavities: Array<{ id: string, name?: string | null, position?: number | null }>, externalIds: Array<{ id: string, source: string }> };

export type JobFieldsFragment = { id: string, name?: string | null, description?: string | null, version?: number | null, standardRate?: string | null, standardRateUnit?: string | null, standardRatePeriod?: RatePeriod | null, standardCycle?: string | null, standardQuantity?: string | null, productsPerCycle?: number | null, profileId?: string | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, tools: Array<{ id: string, name?: string | null }>, items: Array<{ id: string, quantity: number, isActive: boolean, cavityId?: string | null, product?: { id: string, sku?: string | null } | null, tool?: { id: string, name?: string | null } | null }>, eligibleStations: Array<{ id: string, name: string }>, externalIds: Array<{ id: string, source: string }> };

export type OrderFieldsFragment = { id: string, orderNumber: string, poNumber?: string | null, status: OrderStatus, notes?: string | null, customerId?: string | null, defaultTargetQuantity: string, startDate?: string | null, dueDate?: string | null, openedAt?: string | null, completedAt?: string | null, cancelledAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, customer?: { id: string, name: string } | null, lines: Array<{ id: string, productId: string, targetQuantity: string, product?: { id: string, sku?: string | null } | null }>, externalIds: Array<{ id: string, source: string }> };

export type ProductionRunFieldsFragment = { id: string, status: ProductionRunStatus, rank: number, stationId: string, workcenterId: string, jobId: string, startBy?: string | null, endBy?: string | null, startByMissed: boolean, endByMissed: boolean, plannedStart?: string | null, plannedEnd?: string | null, plannedBusinessDate?: string | null, plannedShiftName?: string | null, plannedChangeoverMinutes?: number | null, actualChangeoverMinutes?: number | null, runStartedAt?: string | null, quantityMetAt?: string | null, closedAt?: string | null, closedBusinessDate?: string | null, closeReason?: ProductionRunCloseReason | null, skipCount: number, jobChangedAt?: string | null, createdAt: string, updatedAt: string, station?: { id: string, name: string } | null, job?: { id: string, name?: string | null } | null, parts: Array<{ productId: string, perCycle: number, requiredGood: string, goodCount?: string | null, scrapCount?: string | null, metAt?: string | null, product?: { id: string, sku?: string | null } | null }>, externalIds: Array<{ id: string, source: string }> };

export type EntityModelFieldsFragment = { id: string, key: string, label: string, description?: string | null, version: number, createdAt: string, updatedAt: string, fields: Array<{ key: string, label: string, description?: string | null, type: EntityFieldType, required: boolean, isList: boolean, refModel?: string | null, options?: Array<{ value: string, label?: string | null }> | null }> };

export type EntityRecordFieldsFragment = { id: string, model: string, name: string, values: unknown, deleted: boolean, createdAt: string, updatedAt: string, externalIds: Array<{ id: string, source: string }> };

export type WebhookFieldsFragment = { id: string, url: string, events: Array<WebhookEventType>, enabled: boolean, createdAt: string, updatedAt: string };

export type WebhookDeliveryFieldsFragment = { id: string, eventId?: string | null, type?: string | null, status: WebhookDeliveryStatus, attempts: number, responseStatus?: number | null, error?: string | null, startedAt: string, finishedAt?: string | null, nextAttemptAt?: string | null };

export type UpsertErrorFieldsFragment = { code: string, field?: string | null, message: string };

export type GetSiteQueryVariables = Exact<{ [key: string]: never; }>;


export type GetSiteQuery = { site?: { id: string, name: string, description?: string | null, timezone: string, updatedAt: string } | null };

export type GetWorkcenterQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetWorkcenterQuery = { workcenter?: { id: string, name: string, description?: string | null, parentId?: string | null, createdAt: string, updatedAt: string, externalIds: Array<{ id: string, source: string }> } | null };

export type ListWorkcentersQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  updatedSince?: InputMaybe<Scalars['DateTime']['input']>;
  includeDeleted?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type ListWorkcentersQuery = { workcenters: { nodes: Array<{ id: string, name: string, description?: string | null, parentId?: string | null, createdAt: string, updatedAt: string, externalIds: Array<{ id: string, source: string }> }>, pageInfo: { hasNextPage: boolean, endCursor?: string | null } } };

export type GetStationQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetStationQuery = { station?: { id: string, name: string, description?: string | null, sortOrder: number, workcenterId?: string | null, currentJobId?: string | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, workcenter?: { id: string, name: string } | null, currentJob?: { id: string, name?: string | null } | null, externalIds: Array<{ id: string, source: string }> } | null };

export type ListStationsQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  updatedSince?: InputMaybe<Scalars['DateTime']['input']>;
  includeDeleted?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type ListStationsQuery = { stations: { nodes: Array<{ id: string, name: string, description?: string | null, sortOrder: number, workcenterId?: string | null, currentJobId?: string | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, workcenter?: { id: string, name: string } | null, currentJob?: { id: string, name?: string | null } | null, externalIds: Array<{ id: string, source: string }> }>, pageInfo: { hasNextPage: boolean, endCursor?: string | null } } };

export type GetCustomerQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetCustomerQuery = { customer?: { id: string, name: string, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> } | null };

export type ListCustomersQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  updatedSince?: InputMaybe<Scalars['DateTime']['input']>;
  includeDeleted?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type ListCustomersQuery = { customers: { nodes: Array<{ id: string, name: string, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> }>, pageInfo: { hasNextPage: boolean, endCursor?: string | null } } };

export type GetMaterialQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetMaterialQuery = { material?: { id: string, materialNumber?: string | null, name?: string | null, description?: string | null, classification?: string | null, shortCode?: string | null, externalNumber?: string | null, unitCost?: string | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> } | null };

export type ListMaterialsQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  updatedSince?: InputMaybe<Scalars['DateTime']['input']>;
  includeDeleted?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type ListMaterialsQuery = { materials: { nodes: Array<{ id: string, materialNumber?: string | null, name?: string | null, description?: string | null, classification?: string | null, shortCode?: string | null, externalNumber?: string | null, unitCost?: string | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> }>, pageInfo: { hasNextPage: boolean, endCursor?: string | null } } };

export type GetProductQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetProductQuery = { product?: { id: string, sku?: string | null, name?: string | null, description?: string | null, externalSku?: string | null, itemCost?: string | null, weight?: string | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> } | null };

export type ListProductsQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  updatedSince?: InputMaybe<Scalars['DateTime']['input']>;
  includeDeleted?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type ListProductsQuery = { products: { nodes: Array<{ id: string, sku?: string | null, name?: string | null, description?: string | null, externalSku?: string | null, itemCost?: string | null, weight?: string | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> }>, pageInfo: { hasNextPage: boolean, endCursor?: string | null } } };

export type GetToolQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetToolQuery = { tool?: { id: string, name?: string | null, description?: string | null, cavityCount?: number | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, cavities: Array<{ id: string, name?: string | null, position?: number | null }>, externalIds: Array<{ id: string, source: string }> } | null };

export type ListToolsQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  updatedSince?: InputMaybe<Scalars['DateTime']['input']>;
  includeDeleted?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type ListToolsQuery = { tools: { nodes: Array<{ id: string, name?: string | null, description?: string | null, cavityCount?: number | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, cavities: Array<{ id: string, name?: string | null, position?: number | null }>, externalIds: Array<{ id: string, source: string }> }>, pageInfo: { hasNextPage: boolean, endCursor?: string | null } } };

export type GetJobQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetJobQuery = { job?: { id: string, name?: string | null, description?: string | null, version?: number | null, standardRate?: string | null, standardRateUnit?: string | null, standardRatePeriod?: RatePeriod | null, standardCycle?: string | null, standardQuantity?: string | null, productsPerCycle?: number | null, profileId?: string | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, tools: Array<{ id: string, name?: string | null }>, items: Array<{ id: string, quantity: number, isActive: boolean, cavityId?: string | null, product?: { id: string, sku?: string | null } | null, tool?: { id: string, name?: string | null } | null }>, eligibleStations: Array<{ id: string, name: string }>, externalIds: Array<{ id: string, source: string }> } | null };

export type ListJobsQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  updatedSince?: InputMaybe<Scalars['DateTime']['input']>;
  includeDeleted?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type ListJobsQuery = { jobs: { nodes: Array<{ id: string, name?: string | null, description?: string | null, version?: number | null, standardRate?: string | null, standardRateUnit?: string | null, standardRatePeriod?: RatePeriod | null, standardCycle?: string | null, standardQuantity?: string | null, productsPerCycle?: number | null, profileId?: string | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, tools: Array<{ id: string, name?: string | null }>, items: Array<{ id: string, quantity: number, isActive: boolean, cavityId?: string | null, product?: { id: string, sku?: string | null } | null, tool?: { id: string, name?: string | null } | null }>, eligibleStations: Array<{ id: string, name: string }>, externalIds: Array<{ id: string, source: string }> }>, pageInfo: { hasNextPage: boolean, endCursor?: string | null } } };

export type GetOrderQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetOrderQuery = { order?: { id: string, orderNumber: string, poNumber?: string | null, status: OrderStatus, notes?: string | null, customerId?: string | null, defaultTargetQuantity: string, startDate?: string | null, dueDate?: string | null, openedAt?: string | null, completedAt?: string | null, cancelledAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, customer?: { id: string, name: string } | null, lines: Array<{ id: string, productId: string, targetQuantity: string, product?: { id: string, sku?: string | null } | null }>, externalIds: Array<{ id: string, source: string }> } | null };

export type ListOrdersQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  updatedSince?: InputMaybe<Scalars['DateTime']['input']>;
  includeDeleted?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type ListOrdersQuery = { orders: { nodes: Array<{ id: string, orderNumber: string, poNumber?: string | null, status: OrderStatus, notes?: string | null, customerId?: string | null, defaultTargetQuantity: string, startDate?: string | null, dueDate?: string | null, openedAt?: string | null, completedAt?: string | null, cancelledAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, customer?: { id: string, name: string } | null, lines: Array<{ id: string, productId: string, targetQuantity: string, product?: { id: string, sku?: string | null } | null }>, externalIds: Array<{ id: string, source: string }> }>, pageInfo: { hasNextPage: boolean, endCursor?: string | null } } };

export type GetProductionRunQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetProductionRunQuery = { productionRun?: { id: string, status: ProductionRunStatus, rank: number, stationId: string, workcenterId: string, jobId: string, startBy?: string | null, endBy?: string | null, startByMissed: boolean, endByMissed: boolean, plannedStart?: string | null, plannedEnd?: string | null, plannedBusinessDate?: string | null, plannedShiftName?: string | null, plannedChangeoverMinutes?: number | null, actualChangeoverMinutes?: number | null, runStartedAt?: string | null, quantityMetAt?: string | null, closedAt?: string | null, closedBusinessDate?: string | null, closeReason?: ProductionRunCloseReason | null, skipCount: number, jobChangedAt?: string | null, createdAt: string, updatedAt: string, station?: { id: string, name: string } | null, job?: { id: string, name?: string | null } | null, parts: Array<{ productId: string, perCycle: number, requiredGood: string, goodCount?: string | null, scrapCount?: string | null, metAt?: string | null, product?: { id: string, sku?: string | null } | null }>, externalIds: Array<{ id: string, source: string }> } | null };

export type ListProductionRunsQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  updatedSince?: InputMaybe<Scalars['DateTime']['input']>;
  includeDeleted?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type ListProductionRunsQuery = { productionRuns: { nodes: Array<{ id: string, status: ProductionRunStatus, rank: number, stationId: string, workcenterId: string, jobId: string, startBy?: string | null, endBy?: string | null, startByMissed: boolean, endByMissed: boolean, plannedStart?: string | null, plannedEnd?: string | null, plannedBusinessDate?: string | null, plannedShiftName?: string | null, plannedChangeoverMinutes?: number | null, actualChangeoverMinutes?: number | null, runStartedAt?: string | null, quantityMetAt?: string | null, closedAt?: string | null, closedBusinessDate?: string | null, closeReason?: ProductionRunCloseReason | null, skipCount: number, jobChangedAt?: string | null, createdAt: string, updatedAt: string, station?: { id: string, name: string } | null, job?: { id: string, name?: string | null } | null, parts: Array<{ productId: string, perCycle: number, requiredGood: string, goodCount?: string | null, scrapCount?: string | null, metAt?: string | null, product?: { id: string, sku?: string | null } | null }>, externalIds: Array<{ id: string, source: string }> }>, pageInfo: { hasNextPage: boolean, endCursor?: string | null } } };

export type GetStationLineupQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetStationLineupQuery = { station?: { id: string, name: string, lineup?: Array<{ position: number, predictedChangeoverStart: string, predictedStart: string, predictedEnd: string, startByAtRisk: boolean, endByAtRisk: boolean, progress: Array<{ productId: string, requiredGood: string, good: number, scrap: number }>, run: { id: string, status: ProductionRunStatus, rank: number, stationId: string, workcenterId: string, jobId: string, startBy?: string | null, endBy?: string | null, startByMissed: boolean, endByMissed: boolean, plannedStart?: string | null, plannedEnd?: string | null, plannedBusinessDate?: string | null, plannedShiftName?: string | null, plannedChangeoverMinutes?: number | null, actualChangeoverMinutes?: number | null, runStartedAt?: string | null, quantityMetAt?: string | null, closedAt?: string | null, closedBusinessDate?: string | null, closeReason?: ProductionRunCloseReason | null, skipCount: number, jobChangedAt?: string | null, createdAt: string, updatedAt: string, station?: { id: string, name: string } | null, job?: { id: string, name?: string | null } | null, parts: Array<{ productId: string, perCycle: number, requiredGood: string, goodCount?: string | null, scrapCount?: string | null, metAt?: string | null, product?: { id: string, sku?: string | null } | null }>, externalIds: Array<{ id: string, source: string }> } }> | null } | null };

export type ListEntityModelsQueryVariables = Exact<{ [key: string]: never; }>;


export type ListEntityModelsQuery = { entityModels: Array<{ id: string, key: string, label: string, description?: string | null, version: number, createdAt: string, updatedAt: string, fields: Array<{ key: string, label: string, description?: string | null, type: EntityFieldType, required: boolean, isList: boolean, refModel?: string | null, options?: Array<{ value: string, label?: string | null }> | null }> }> };

export type GetEntityModelQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetEntityModelQuery = { entityModel?: { id: string, key: string, label: string, description?: string | null, version: number, createdAt: string, updatedAt: string, fields: Array<{ key: string, label: string, description?: string | null, type: EntityFieldType, required: boolean, isList: boolean, refModel?: string | null, options?: Array<{ value: string, label?: string | null }> | null }> } | null };

export type GetEntityRecordQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetEntityRecordQuery = { entityRecord?: { id: string, model: string, name: string, values: unknown, deleted: boolean, createdAt: string, updatedAt: string, externalIds: Array<{ id: string, source: string }> } | null };

export type ListEntityRecordsQueryVariables = Exact<{
  model: Scalars['String']['input'];
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  updatedSince?: InputMaybe<Scalars['DateTime']['input']>;
  includeDeleted?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type ListEntityRecordsQuery = { entityRecords: { nodes: Array<{ id: string, model: string, name: string, values: unknown, deleted: boolean, createdAt: string, updatedAt: string, externalIds: Array<{ id: string, source: string }> }>, pageInfo: { hasNextPage: boolean, endCursor?: string | null } } };

export type ListWebhooksQueryVariables = Exact<{ [key: string]: never; }>;


export type ListWebhooksQuery = { webhooks: Array<{ id: string, url: string, events: Array<WebhookEventType>, enabled: boolean, createdAt: string, updatedAt: string }> };

export type ListWebhookDeliveriesQueryVariables = Exact<{
  webhookId: Scalars['ID']['input'];
  status?: InputMaybe<WebhookDeliveryStatus>;
  first?: InputMaybe<Scalars['Int']['input']>;
}>;


export type ListWebhookDeliveriesQuery = { webhookDeliveries: Array<{ id: string, eventId?: string | null, type?: string | null, status: WebhookDeliveryStatus, attempts: number, responseStatus?: number | null, error?: string | null, startedAt: string, finishedAt?: string | null, nextAttemptAt?: string | null }> };

export type CreateWebhookMutationVariables = Exact<{
  webhook: WebhookInput;
}>;


export type CreateWebhookMutation = { createWebhook: { secret: string, webhook: { id: string, url: string, events: Array<WebhookEventType>, enabled: boolean, createdAt: string, updatedAt: string } } };

export type UpdateWebhookMutationVariables = Exact<{
  id: Scalars['ID']['input'];
  webhook: WebhookUpdateInput;
}>;


export type UpdateWebhookMutation = { updateWebhook: { id: string, url: string, events: Array<WebhookEventType>, enabled: boolean, createdAt: string, updatedAt: string } };

export type DeleteWebhookMutationVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type DeleteWebhookMutation = { deleteWebhook: boolean };

export type RotateWebhookSecretMutationVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type RotateWebhookSecretMutation = { rotateWebhookSecret: { secret: string, webhook: { id: string, url: string, events: Array<WebhookEventType>, enabled: boolean, createdAt: string, updatedAt: string } } };

export type SendTestWebhookMutationVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type SendTestWebhookMutation = { sendTestWebhook: { id: string, eventId?: string | null, type?: string | null, status: WebhookDeliveryStatus, attempts: number, responseStatus?: number | null, error?: string | null, startedAt: string, finishedAt?: string | null, nextAttemptAt?: string | null } };

export type RedeliverWebhookMutationVariables = Exact<{
  deliveryId: Scalars['ID']['input'];
}>;


export type RedeliverWebhookMutation = { redeliverWebhook: { id: string, eventId?: string | null, type?: string | null, status: WebhookDeliveryStatus, attempts: number, responseStatus?: number | null, error?: string | null, startedAt: string, finishedAt?: string | null, nextAttemptAt?: string | null } };

export type UpsertWorkcentersMutationVariables = Exact<{
  workcenters: Array<WorkcenterInput> | WorkcenterInput;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type UpsertWorkcentersMutation = { upsertWorkcenters: { results: Array<{ externalId: string, action: UpsertAction, workcenter?: { id: string, name: string, description?: string | null, parentId?: string | null, createdAt: string, updatedAt: string, externalIds: Array<{ id: string, source: string }> } | null }>, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type UpsertStationsMutationVariables = Exact<{
  stations: Array<StationInput> | StationInput;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type UpsertStationsMutation = { upsertStations: { results: Array<{ externalId: string, action: UpsertAction, station?: { id: string, name: string, description?: string | null, sortOrder: number, workcenterId?: string | null, currentJobId?: string | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, workcenter?: { id: string, name: string } | null, currentJob?: { id: string, name?: string | null } | null, externalIds: Array<{ id: string, source: string }> } | null }>, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type UpsertCustomersMutationVariables = Exact<{
  customers: Array<CustomerUpsertInput> | CustomerUpsertInput;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type UpsertCustomersMutation = { upsertCustomers: { results: Array<{ externalId: string, action: UpsertAction, customer?: { id: string, name: string, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> } | null }>, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type UpsertMaterialsMutationVariables = Exact<{
  materials: Array<MaterialInput> | MaterialInput;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type UpsertMaterialsMutation = { upsertMaterials: { results: Array<{ externalId: string, action: UpsertAction, material?: { id: string, materialNumber?: string | null, name?: string | null, description?: string | null, classification?: string | null, shortCode?: string | null, externalNumber?: string | null, unitCost?: string | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> } | null }>, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type UpsertProductsMutationVariables = Exact<{
  products: Array<ProductInput> | ProductInput;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type UpsertProductsMutation = { upsertProducts: { results: Array<{ externalId: string, action: UpsertAction, product?: { id: string, sku?: string | null, name?: string | null, description?: string | null, externalSku?: string | null, itemCost?: string | null, weight?: string | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, externalIds: Array<{ id: string, source: string }> } | null }>, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type UpsertToolsMutationVariables = Exact<{
  tools: Array<ToolInput> | ToolInput;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type UpsertToolsMutation = { upsertTools: { results: Array<{ externalId: string, action: UpsertAction, tool?: { id: string, name?: string | null, description?: string | null, cavityCount?: number | null, version?: number | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, cavities: Array<{ id: string, name?: string | null, position?: number | null }>, externalIds: Array<{ id: string, source: string }> } | null }>, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type UpsertJobsMutationVariables = Exact<{
  jobs: Array<JobInput> | JobInput;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type UpsertJobsMutation = { upsertJobs: { results: Array<{ externalId: string, action: UpsertAction, job?: { id: string, name?: string | null, description?: string | null, version?: number | null, standardRate?: string | null, standardRateUnit?: string | null, standardRatePeriod?: RatePeriod | null, standardCycle?: string | null, standardQuantity?: string | null, productsPerCycle?: number | null, profileId?: string | null, archivedAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, tools: Array<{ id: string, name?: string | null }>, items: Array<{ id: string, quantity: number, isActive: boolean, cavityId?: string | null, product?: { id: string, sku?: string | null } | null, tool?: { id: string, name?: string | null } | null }>, eligibleStations: Array<{ id: string, name: string }>, externalIds: Array<{ id: string, source: string }> } | null }>, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type UpsertProductionRunsMutationVariables = Exact<{
  runs: Array<ProductionRunInput> | ProductionRunInput;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type UpsertProductionRunsMutation = { upsertProductionRuns: { results: Array<{ externalId: string, action: UpsertAction, run?: { id: string, status: ProductionRunStatus, rank: number, stationId: string, workcenterId: string, jobId: string, startBy?: string | null, endBy?: string | null, startByMissed: boolean, endByMissed: boolean, plannedStart?: string | null, plannedEnd?: string | null, plannedBusinessDate?: string | null, plannedShiftName?: string | null, plannedChangeoverMinutes?: number | null, actualChangeoverMinutes?: number | null, runStartedAt?: string | null, quantityMetAt?: string | null, closedAt?: string | null, closedBusinessDate?: string | null, closeReason?: ProductionRunCloseReason | null, skipCount: number, jobChangedAt?: string | null, createdAt: string, updatedAt: string, station?: { id: string, name: string } | null, job?: { id: string, name?: string | null } | null, parts: Array<{ productId: string, perCycle: number, requiredGood: string, goodCount?: string | null, scrapCount?: string | null, metAt?: string | null, product?: { id: string, sku?: string | null } | null }>, externalIds: Array<{ id: string, source: string }> } | null }>, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type UpsertOrderMutationVariables = Exact<{
  order: OrderInput;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type UpsertOrderMutation = { upsertOrder: { action?: UpsertAction | null, order?: { id: string, orderNumber: string, poNumber?: string | null, status: OrderStatus, notes?: string | null, customerId?: string | null, defaultTargetQuantity: string, startDate?: string | null, dueDate?: string | null, openedAt?: string | null, completedAt?: string | null, cancelledAt?: string | null, createdAt: string, updatedAt: string, deletedAt?: string | null, customer?: { id: string, name: string } | null, lines: Array<{ id: string, productId: string, targetQuantity: string, product?: { id: string, sku?: string | null } | null }>, externalIds: Array<{ id: string, source: string }> } | null, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type SequenceLineupMutationVariables = Exact<{
  station: Scalars['String']['input'];
  runs: Array<Scalars['String']['input']> | Scalars['String']['input'];
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type SequenceLineupMutation = { sequenceLineup: { action?: UpsertAction | null, station?: { id: string, name: string } | null, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type LinkExternalIdsMutationVariables = Exact<{
  kind: ExternalIdKind;
  links: Array<ExternalIdLinkInput> | ExternalIdLinkInput;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type LinkExternalIdsMutation = { linkExternalIds: { results: Array<{ id: string, externalId: string, action: UpsertAction }>, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type UpsertEntityModelsMutationVariables = Exact<{
  models: Array<EntityModelInput> | EntityModelInput;
}>;


export type UpsertEntityModelsMutation = { upsertEntityModels: { results: Array<{ key: string, action: UpsertAction, model?: { id: string, key: string, label: string, description?: string | null, version: number, createdAt: string, updatedAt: string, fields: Array<{ key: string, label: string, description?: string | null, type: EntityFieldType, required: boolean, isList: boolean, refModel?: string | null, options?: Array<{ value: string, label?: string | null }> | null }> } | null }>, errors: Array<{ code: string, field?: string | null, message: string }> } };

export type UpsertEntityRecordsMutationVariables = Exact<{
  model: Scalars['String']['input'];
  records: Array<EntityRecordInput> | EntityRecordInput;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type UpsertEntityRecordsMutation = { upsertEntityRecords: { results: Array<{ externalId: string, action: UpsertAction, record?: { id: string, model: string, name: string, values: unknown, deleted: boolean, createdAt: string, updatedAt: string, externalIds: Array<{ id: string, source: string }> } | null }>, errors: Array<{ code: string, field?: string | null, message: string }> } };
