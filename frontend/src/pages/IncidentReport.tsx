import { FormEvent, useState } from "react";
import { Button, GlassCard, PageHeader } from "../components/common";

export default function IncidentReport() {
  const [state, setState] = useState<"idle" | "saved">("idle");

  function save(e: FormEvent) {
    e.preventDefault();
    setState("saved");
  }

  return (
    <section className="reveal space-y-6">
      <PageHeader
        title="Field incident report"
        eyebrow="Field intake"
        description="Drafts stay in this browser session. Nothing is transmitted from this screen."
      />

      <form onSubmit={save} className="space-y-4">
        <GlassCard className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="incident-title" className="hud-label">
              Incident title
            </label>
            <input
              id="incident-title"
              required
              placeholder="Incident title"
              className="glass-field"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="incident-hazard" className="hud-label">
              Hazard type
            </label>
            <select id="incident-hazard" className="glass-field">
              <option className="bg-background-deep text-white">Flood</option>
              <option className="bg-background-deep text-white">Rainfall</option>
              <option className="bg-background-deep text-white">Landslide</option>
            </select>
          </div>

          <div className="space-y-2">
            <label htmlFor="incident-notes" className="hud-label">
              Situation notes
            </label>
            <textarea
              id="incident-notes"
              required
              placeholder="Situation, location, and observed impact"
              className="glass-field min-h-36 resize-y"
            />
          </div>

          <Button type="submit" size="lg">
            Save local draft
          </Button>
        </GlassCard>
      </form>

      {state === "saved" && (
        <GlassCard>
          <p className="text-sm text-[#FFB547]">
            Draft saved in this browser session. It has not been transmitted: the current backend does not expose an
            incident-report endpoint.
          </p>
        </GlassCard>
      )}

      <p className="text-sm text-muted-text">
        This screen intentionally does not claim a report was sent until an incident-ingest API is added.
      </p>
    </section>
  );
}
