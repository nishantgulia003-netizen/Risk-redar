import { FormEvent, useState } from "react";
import { postAskAI, type AskAI } from "../lib/api";
import { Button, GlassCard, PageHeader } from "../components/common";

export default function AIAssistant() {
  const [q, setQ] = useState("Which area should we evacuate first and why?");
  const [result, setResult] = useState<AskAI>();
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);

  async function ask(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(undefined);
    try {
      setResult(await postAskAI(q));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="reveal space-y-6">
      <PageHeader
        title="AI decision assistant"
        eyebrow="Grounded operational assistant"
        description="Answers are grounded only in current RiskRadar data. Retrieved source data is shown below every answer."
      />

      <form onSubmit={ask} className="space-y-3">
        <GlassCard className="space-y-3">
          <label htmlFor="ask-ai-question" className="hud-label">
            Question
          </label>
          <textarea
            id="ask-ai-question"
            className="glass-field min-h-28 resize-y"
            value={q}
            maxLength={1000}
            onChange={(e) => setQ(e.target.value)}
          />
          <Button type="submit" loading={loading} size="lg" className="w-full sm:w-auto">
            {loading ? "Retrieving…" : "Ask RiskRadar"}
          </Button>
        </GlassCard>
      </form>

      {error && (
        <GlassCard variant="critical">
          <p className="text-sm font-mono text-bright-red">{error}</p>
        </GlassCard>
      )}

      {result && (
        <>
          <GlassCard>
            <p className="hud-label text-[#FFB547]">Grounded answer</p>
            <p className="mt-2 whitespace-pre-wrap leading-6 text-white">{result.answer}</p>
          </GlassCard>
          <GlassCard variant="subtle">
            <details>
              <summary className="cursor-pointer font-bold text-white">Data used for this answer</summary>
              <pre className="mt-3 overflow-auto text-xs font-mono text-muted-text">
                {JSON.stringify(result.sources, null, 2)}
              </pre>
            </details>
          </GlassCard>
        </>
      )}
    </section>
  );
}
