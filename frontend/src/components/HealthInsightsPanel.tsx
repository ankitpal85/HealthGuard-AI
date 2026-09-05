import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Footprints,
  HeartPulse,
  Moon,
  Pill,
  RefreshCw,
} from "lucide-react";

type Insight = {
  type: "positive" | "warning" | "info";
  title: string;
  message: string;
};

type HealthInsights = {
  wellness_score: number;
  level: string;
  data_points: {
    vitals_7day: number;
    active_medications: number;
    nutrition_logs_7day: number;
    adherence_7day: number;
  };
  insights: Insight[];
  recommendations: string[];
  disclaimer: string;
};

type Props = {
  userId: number;
};

const API_BASE = import.meta.env.VITE_API_URL || "";

export function HealthInsightsPanel({ userId }: Props) {
  const [data, setData] = useState<HealthInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadInsights = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_BASE}/api/health-insights?user_id=${encodeURIComponent(userId)}`
      );

      if (!response.ok) {
        throw new Error("Unable to load health insights");
      }

      const payload = await response.json();
      setData(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInsights();
  }, [userId]);

  if (loading) {
    return (
      <section className="mt-6 rounded-2xl border border-slate-200/70 bg-white/80 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/70">
        <div className="flex items-center gap-3">
          <RefreshCw className="h-5 w-5 animate-spin" />
          <p className="text-sm text-slate-500">Generating your health snapshot…</p>
        </div>
      </section>
    );
  }

  if (error || !data) {
    return (
      <section className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-5 dark:border-rose-900/40 dark:bg-rose-950/20">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="font-semibold text-rose-700 dark:text-rose-300">
              Health insights unavailable
            </p>
            <p className="mt-1 text-sm text-rose-600/80 dark:text-rose-300/70">
              {error || "Please try again."}
            </p>
          </div>
          <button
            onClick={loadInsights}
            className="rounded-lg border border-rose-300 px-3 py-2 text-sm font-medium hover:bg-white dark:border-rose-800 dark:hover:bg-rose-950"
          >
            Retry
          </button>
        </div>
      </section>
    );
  }

  const scoreRing =
    data.wellness_score >= 85
      ? "border-emerald-500 text-emerald-600"
      : data.wellness_score >= 70
        ? "border-amber-500 text-amber-600"
        : "border-rose-500 text-rose-600";

  const insightIcon = (type: Insight["type"]) => {
    if (type === "positive") {
      return <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-500" />;
    }
    if (type === "warning") {
      return <AlertTriangle className="h-5 w-5 shrink-0 text-amber-500" />;
    }
    return <Activity className="h-5 w-5 shrink-0 text-sky-500" />;
  };

  return (
    <section className="mt-6 space-y-5">
      <div className="rounded-2xl border border-slate-200/70 bg-white/80 p-6 shadow-sm backdrop-blur dark:border-slate-800 dark:bg-slate-900/70">
        <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <HeartPulse className="h-5 w-5 text-sky-500" />
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                Smart Health Snapshot
              </h2>
            </div>
            <p className="mt-1 text-sm text-slate-500">
              Explainable insights generated from your recent HealthGuard data.
            </p>
          </div>

          <button
            onClick={loadInsights}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium transition hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-[150px_1fr]">
          <div className="flex items-center justify-center">
            <div
              className={`flex h-32 w-32 flex-col items-center justify-center rounded-full border-8 bg-slate-50 dark:bg-slate-950 ${scoreRing}`}
            >
              <span className="text-3xl font-extrabold">
                {data.wellness_score}
              </span>
              <span className="text-xs font-semibold uppercase tracking-wide">
                {data.level}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <MetricCard
              icon={<Activity className="h-4 w-4" />}
              label="Vitals"
              value={`${data.data_points.vitals_7day}`}
              suffix="records"
            />
            <MetricCard
              icon={<Pill className="h-4 w-4" />}
              label="Adherence"
              value={`${data.data_points.adherence_7day}`}
              suffix="%"
            />
            <MetricCard
              icon={<Footprints className="h-4 w-4" />}
              label="Medications"
              value={`${data.data_points.active_medications}`}
              suffix="active"
            />
            <MetricCard
              icon={<Moon className="h-4 w-4" />}
              label="Nutrition"
              value={`${data.data_points.nutrition_logs_7day}`}
              suffix="logs"
            />
          </div>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200/70 bg-white/80 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/70">
          <h3 className="font-bold text-slate-900 dark:text-white">What the system noticed</h3>
          <div className="mt-4 space-y-3">
            {data.insights.map((item, index) => (
              <div
                key={`${item.title}-${index}`}
                className="flex gap-3 rounded-xl bg-slate-50 p-3 dark:bg-slate-950/60"
              >
                {insightIcon(item.type)}
                <div>
                  <p className="text-sm font-semibold text-slate-900 dark:text-white">
                    {item.title}
                  </p>
                  <p className="mt-1 text-sm leading-5 text-slate-500">
                    {item.message}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200/70 bg-white/80 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/70">
          <h3 className="font-bold text-slate-900 dark:text-white">Recommended next steps</h3>
          <div className="mt-4 space-y-3">
            {data.recommendations.map((recommendation, index) => (
              <div key={index} className="flex gap-3">
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-sky-100 text-xs font-bold text-sky-700 dark:bg-sky-950 dark:text-sky-300">
                  {index + 1}
                </span>
                <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">
                  {recommendation}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <p className="px-1 text-xs leading-5 text-slate-400">{data.disclaimer}</p>
    </section>
  );
}

function MetricCard({
  icon,
  label,
  value,
  suffix,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  suffix: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-800">
      <div className="flex items-center gap-2 text-slate-500">
        {icon}
        <span className="text-xs font-medium uppercase tracking-wide">{label}</span>
      </div>
      <div className="mt-2">
        <span className="text-xl font-bold text-slate-900 dark:text-white">{value}</span>
        <span className="ml-1 text-xs text-slate-500">{suffix}</span>
      </div>
    </div>
  );
}
