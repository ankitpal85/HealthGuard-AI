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
  Sparkles,
} from "lucide-react";
import { fetchHealthInsights } from "../services/api";

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

export function HealthInsightsPanel({ userId }: Props) {
  const [data, setData] = useState<HealthInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadInsights = async () => {
    setLoading(true);
    setError("");

    try {
      const payload = await fetchHealthInsights(userId);
      setData(payload);
    } catch (err: any) {
      console.error("Health insights load error:", err);
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        "Unable to connect to health insights service.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInsights();
  }, [userId]);

  if (loading) {
    return (
      <section className="glass-panel mt-7 rounded-3xl p-6 shadow-xl border border-sky-500/20 bg-slate-900/60 backdrop-blur-xl">
        <div className="flex items-center gap-3 text-sky-400 font-medium text-sm">
          <RefreshCw className="h-5 w-5 animate-spin" />
          <p>Generating real-time smart health insights…</p>
        </div>
      </section>
    );
  }

  if (error || !data) {
    return (
      <section className="glass-panel mt-7 rounded-3xl p-6 shadow-xl border border-rose-500/30 bg-rose-950/20 backdrop-blur-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-6 w-6 shrink-0 text-rose-400 mt-0.5" />
            <div>
              <p className="font-semibold text-rose-300">
                Health insights temporarily unavailable
              </p>
              <p className="mt-1 text-sm text-rose-400/80">
                {error || "Could not retrieve clinical insights. Please ensure the backend is running."}
              </p>
            </div>
          </div>
          <button
            onClick={loadInsights}
            className="self-start sm:self-center inline-flex items-center gap-2 rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-2 text-sm font-medium text-rose-300 hover:bg-rose-500/20 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            Retry
          </button>
        </div>
      </section>
    );
  }

  const scoreColor =
    data.wellness_score >= 80
      ? "text-emerald-400 border-emerald-500/60 shadow-[0_0_20px_rgba(16,185,129,0.25)]"
      : data.wellness_score >= 50
        ? "text-amber-400 border-amber-500/60 shadow-[0_0_20px_rgba(245,158,11,0.25)]"
        : "text-rose-400 border-rose-500/60 shadow-[0_0_20px_rgba(244,63,94,0.25)]";

  const insightIcon = (type: Insight["type"]) => {
    if (type === "positive") {
      return <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-400" />;
    }
    if (type === "warning") {
      return <AlertTriangle className="h-5 w-5 shrink-0 text-amber-400" />;
    }
    return <Activity className="h-5 w-5 shrink-0 text-sky-400" />;
  };

  return (
    <section className="mt-7 space-y-6 animate-in fade-in duration-300">
      {/* Overview Card */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 shadow-2xl border border-sky-500/20 bg-slate-900/60 backdrop-blur-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-80 h-80 rounded-full blur-3xl pointer-events-none opacity-20 bg-sky-500" />

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-sky-500/10 border border-sky-500/30 text-sky-400">
                <HeartPulse className="h-5 w-5" />
              </div>
              <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                Smart Health Insights
                <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-300 font-semibold border border-sky-500/30 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> AI
                </span>
              </h2>
            </div>
            <p className="mt-1 text-sm text-slate-400">
              Personalized wellness telemetry and clinical adherence overview.
            </p>
          </div>

          <button
            onClick={loadInsights}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-slate-700 hover:text-white"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>

        <div className="mt-6 grid gap-6 md:grid-cols-[180px_1fr] items-center">
          {/* Circular Score */}
          <div className="flex flex-col items-center justify-center p-4">
            <div
              className={`flex h-32 w-32 flex-col items-center justify-center rounded-full border-4 bg-slate-950/80 ${scoreColor}`}
            >
              <span className="text-3xl font-extrabold tracking-tight">
                {data.wellness_score}
              </span>
              <span className="text-[10px] font-bold uppercase tracking-wider mt-0.5 opacity-90">
                Score
              </span>
            </div>
            <span className="mt-2 text-xs font-semibold uppercase tracking-wider text-slate-300">
              {data.level}
            </span>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <MetricCard
              icon={<Activity className="h-4 w-4 text-sky-400" />}
              label="7-Day Vitals"
              value={`${data.data_points.vitals_7day}`}
              suffix="logs"
            />
            <MetricCard
              icon={<Pill className="h-4 w-4 text-emerald-400" />}
              label="Adherence"
              value={`${data.data_points.adherence_7day}`}
              suffix="%"
            />
            <MetricCard
              icon={<Footprints className="h-4 w-4 text-purple-400" />}
              label="Medications"
              value={`${data.data_points.active_medications}`}
              suffix="active"
            />
            <MetricCard
              icon={<Moon className="h-4 w-4 text-amber-400" />}
              label="Nutrition"
              value={`${data.data_points.nutrition_logs_7day}`}
              suffix="meals"
            />
          </div>
        </div>
      </div>

      {/* Insights & Recommendations Dual Columns */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* System Observations */}
        <div className="glass-panel rounded-3xl p-6 shadow-xl border border-slate-800 bg-slate-900/60 backdrop-blur-xl">
          <h3 className="font-bold text-white flex items-center gap-2 text-base">
            <span className="w-2 h-2 rounded-full bg-sky-400"></span>
            System Observations
          </h3>
          <div className="mt-4 space-y-3">
            {data.insights.map((item, index) => (
              <div
                key={`${item.title}-${index}`}
                className="flex gap-3 rounded-2xl bg-slate-950/60 border border-slate-800/80 p-3.5"
              >
                {insightIcon(item.type)}
                <div>
                  <p className="text-sm font-semibold text-slate-100">
                    {item.title}
                  </p>
                  <p className="mt-1 text-xs sm:text-sm leading-relaxed text-slate-400">
                    {item.message}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recommended Next Steps */}
        <div className="glass-panel rounded-3xl p-6 shadow-xl border border-slate-800 bg-slate-900/60 backdrop-blur-xl">
          <h3 className="font-bold text-white flex items-center gap-2 text-base">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Recommended Next Steps
          </h3>
          <div className="mt-4 space-y-3">
            {data.recommendations.map((recommendation, index) => (
              <div
                key={index}
                className="flex gap-3 rounded-2xl bg-slate-950/60 border border-slate-800/80 p-3.5 items-start"
              >
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-sky-500/20 text-xs font-bold text-sky-400 border border-sky-500/30">
                  {index + 1}
                </span>
                <p className="text-xs sm:text-sm leading-relaxed text-slate-300">
                  {recommendation}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <p className="px-2 text-xs leading-relaxed text-slate-500 italic">
        * {data.disclaimer}
      </p>
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
    <div className="rounded-2xl border border-slate-800/80 bg-slate-950/60 p-4 transition hover:border-slate-700">
      <div className="flex items-center gap-2 text-slate-400">
        {icon}
        <span className="text-[11px] font-semibold uppercase tracking-wider">
          {label}
        </span>
      </div>
      <div className="mt-2.5 flex items-baseline">
        <span className="text-2xl font-bold text-white tracking-tight">
          {value}
        </span>
        <span className="ml-1 text-xs text-slate-400">{suffix}</span>
      </div>
    </div>
  );
}
