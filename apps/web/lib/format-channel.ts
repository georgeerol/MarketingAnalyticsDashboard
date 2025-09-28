/**
 * Formats channel names for display
 * Converts "Channel0" to "Channel 0", "Channel1" to "Channel 1", etc.
 * Also handles underscores by replacing them with spaces
 */
export function formatChannelName(channelName: string): string {
  return channelName
    .replace(/_/g, " ") // Replace underscores with spaces
    .replace(/([a-zA-Z])(\d)/g, "$1 $2"); // Add space between letters and numbers
}
