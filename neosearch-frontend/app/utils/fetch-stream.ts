/**
 * Pass the data from reader to controller.
 * This function is called recursively until the reader is done.
 * When the reader is done, the controller is closed.
 * Otherwise, the data is passed to the controller and the function is called again.
 *
 * @param reader The reader to read data from.
 * @param controller The controller to pass the data to.
 * @param onChunk The callback to call when a chunk is read.
 * @param onDone The callback to call when the reader is done.
 * @returns A promise that resolves when the reader is done.
 */
async function pump(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  controller: ReadableStreamDefaultController,
  onChunk?: (chunk: Uint8Array) => void,
  onDone?: () => void,
): Promise<ReadableStreamReadResult<Uint8Array> | undefined> {
  const { done, value } = await reader.read();
  if (done) {
    onDone && onDone();
    controller.close();
    return;
  }
  onChunk && onChunk(value);
  controller.enqueue(value);
  return pump(reader, controller, onChunk, onDone);
};

/**
 * Fetch a stream from the given response.
 *
 * @param response The response to fetch the stream from.
 * @param onChunk The callback to call when a chunk is read.
 * @param onDone The callback to call when the reader is done.
 * @returns The stream.
 */
export const fetchStream = (
  response: Response,
  onChunk?: (chunk: Uint8Array) => void,
  onDone?: () => void,
): ReadableStream<string> => {
  const reader = response.body!.getReader();
  return new ReadableStream({
    start: (controller) => pump(reader, controller, onChunk, onDone),
  });
};
