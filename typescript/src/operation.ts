// Shapes shared by the generated methods and the client that sends them.

/** One operation from operations/, ready to send. */
export interface Operation {
  name: string;
  /** The one field it asks for; its value is what the method returns. */
  root: string;
  mutation: boolean;
  /** Sending it twice gives the same result as once, so it can be retried. */
  safeToRepeat: boolean;
  /** The operation and the fragments it uses. */
  document: string;
}

export interface CallOptions {
  /** Stops the call, including any wait before a retry. */
  signal?: AbortSignal;
}

export interface PageOptions extends CallOptions {
  /** Stop after this many pages. Default 10,000. */
  maxPages?: number;
}
