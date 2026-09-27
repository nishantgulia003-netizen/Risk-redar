import { LoadingState } from "./common/LoadingState";
import { ErrorState as CommonErrorState } from "./common/ErrorState";

export function Loading({ label = "Loading live operational data" }: { label?: string }) {
  return <LoadingState label={label} />;
}

export function ErrorState({ error, retry }: { error: string; retry?: () => void }) {
  return <CommonErrorState error={error} retry={retry} />;
}
