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
      <section
        className="glass-panel mt-7 p-6 shadow-xl rounded-3xl"
        style={{ border: "1px solid var(--border-color)" }}
      >
        <div
          className="flex items-center gap-3 font-semibold text-sm"
          style={{ color: "#0EA5E9" }}
        >
          <RefreshCw className="h-5 w-5 animate-spin" />
          <p>Generating real-time smart health insights…</p>
        </div>
      </section>
    );
  }

  if (error || !data) {
    return (
      <section
        className="glass-panel mt-7 p-6 shadow-xl rounded-3xl"
        style={{
          border: "1px solid rgba(239,68,68,0.3)",
          background: "rgba(239,68,68,0.06)",
        }}
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-rose-500/15 text-rose-500 mt-0.5">
              <AlertTriangle className="h-5 w-5 shrink-0" />
            </div>
            <div>
              <p className="font-bold text-rose-600 dark:text-rose-400">
                Health insights temporarily unavailable
              </p>
              <p className="mt-1 text-xs font-medium text-rose-500/80">
                {error || "Could not retrieve clinical insights. Please ensure the backend is running."}
              </p>
            </div>
          </div>
          <button
            onClick={loadInsights}
            className="self-start sm:self-center inline-flex items-center gap-2 rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-2 text-xs font-bold text-rose-600 dark:text-rose-300 hover:bg-rose-500/20 transition-all cursor-pointer"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Retry
          </button>
        </div>
      </section>
    );
  }

  const scoreConfig =
    data.wellness_score >= 80
      ? {
          ring: "#10B981",
          border: "border-emerald-500",
          badgeBg: "rgba(16,185,129,0.12)",
          badgeBorder: "rgba(16,185,129,0.3)",
          glow: "0 0 24px rgba(16,185,129,0.25)",
        }
      : data.wellness_score >= 50
        ? {
            ring: "#F59E0B",
            border: "border-amber-500",
            badgeBg: "rgba(245,158,11,0.12)",
            badgeBorder: "rgba(245,158,11,0.3)",
            glow: "0 0 24px rgba(245,158,11,0.25)",
          }
        : {
            ring: "#EF4444",
            border: "border-rose-500",
            badgeBg: "rgba(239,68,68,0.12)",
            badgeBorder: "rgba(239,68,68,0.3)",
            glow: "0 0 24px rgba(239,68,68,0.25)",
          };

  return (
    <section className="mt-7 space-y-6 animate-in fade-in duration-300">
      {/* Overview Card */}
      <div
        className="glass-panel rounded-3xl p-6 sm:p-8 shadow-xl relative overflow-hidden transition-all duration-300"
        style={{
          border: "1px solid var(--border-color)",
        }}
      >
        <div
          className="absolute right-0 top-0 w-80 h-80 rounded-full blur-3xl pointer-events-none opacity-25"
          style={{ background: "radial-gradient(circle, #0EA5E9, transparent)" }}
        />

        <div className="relative z-10 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2.5">
              <div
                className="p-2 rounded-xl flex items-center justify-center"
                style={{
                  background: "rgba(14,165,233,0.15)",
                  border: "1px solid rgba(14,165,233,0.3)",
                  color: "#0EA5E9",
                }}
              >
                <HeartPulse className="h-5 w-5" />
              </div>
              <h2
                className="text-xl font-extrabold tracking-tight flex items-center gap-2"
                style={{
                  color: "var(--text-primary)",
                  fontFamily: "Plus Jakarta Sans, sans-serif",
                }}
              >
                Smart Health Insights
                <span
                  className="text-[11px] px-2.5 py-0.5 rounded-full font-extrabold flex items-center gap-1"
                  style={{
                    background: "rgba(14,165,233,0.15)",
                    border: "1px solid rgba(14,165,233,0.3)",
                    color: "#0EA5E9",
                  }}
                >
                  <Sparkles className="w-3 h-3" /> AI
                </span>
              </h2>
            </div>
            <p
              className="mt-1 text-xs font-semibold"
              style={{ color: "var(--text-muted)" }}
            >
              Personalized wellness telemetry and clinical adherence overview.
            </p>
          </div>

          <button
            onClick={loadInsights}
            className="btn-secondary self-start sm:self-center px-4 py-2 text-xs font-extrabold flex items-center gap-2 cursor-pointer shadow-sm hover:scale-105 transition-all"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>

        <div className="relative z-10 mt-6 grid gap-6 md:grid-cols-[180px_1fr] items-center">
          {/* Circular Score */}
          <div className="flex flex-col items-center justify-center p-2">
            <div
              className="flex h-32 w-32 flex-col items-center justify-center rounded-full border-4 shadow-xl transition-all duration-300"
              style={{
                background: "var(--bg-surface)",
                borderColor: scoreConfig.ring,
                boxShadow: scoreConfig.glow,
              }}
            >
              <span
                className="text-3xl font-black tracking-tight"
                style={{ color: scoreConfig.ring, fontFamily: "Plus Jakarta Sans, sans-serif" }}
              >
                {data.wellness_score}
              </span>
              <span
                className="text-[10px] font-bold uppercase tracking-wider mt-0.5"
                style={{ color: "var(--text-muted)" }}
              >
                Score
              </span>
            </div>
            <span
              className="mt-3 px-3 py-1 text-[11px] font-extrabold uppercase tracking-wider rounded-full shadow-sm text-center"
              style={{
                background: scoreConfig.badgeBg,
                border: `1px solid ${scoreConfig.badgeBorder}`,
                color: scoreConfig.ring,
              }}
            >
              {data.level}
            </span>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
            <MetricCard
              icon={<Activity className="h-4 w-4" style={{ color: "#0EA5E9" }} />}
              iconBg="rgba(14,165,233,0.15)"
              label="7-Day Vitals"
              value={`${data.data_points.vitals_7day}`}
              suffix="logs"
            />
            <MetricCard
              icon={<Pill className="h-4 w-4" style={{ color: "#06D6A0" }} />}
              iconBg="rgba(6,214,160,0.15)"
              label="Adherence"
              value={`${data.data_points.adherence_7day}`}
              suffix="%"
            />
            <MetricCard
              icon={<Footprints className="h-4 w-4" style={{ color: "#8B5CF6" }} />}
              iconBg="rgba(139,92,246,0.15)"
              label="Medications"
              value={`${data.data_points.active_medications}`}
              suffix="active"
            />
            <MetricCard
              icon={<Moon className="h-4 w-4" style={{ color: "#F59E0B" }} />}
              iconBg="rgba(245,158,11,0.15)"
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
        <div
          className="glass-panel rounded-3xl p-6 sm:p-7 space-y-4 shadow-xl"
          style={{ border: "1px solid var(--border-color)" }}
        >
          <h3
            className="font-extrabold flex items-center gap-2 text-base"
            style={{ color: "var(--text-primary)", fontFamily: "Plus Jakarta Sans, sans-serif" }}
          >
            <span className="w-2.5 h-2.5 rounded-full bg-sky-500 shadow-[0_0_8px_rgba(14,165,233,0.6)]"></span>
            System Observations
          </h3>

          <div className="mt-4 space-y-3">
            {data.insights.map((item, index) => {
              const isWarning = item.type === "warning";
              const isPositive = item.type === "positive";

              const tintStyle = isPositive
                ? {
                    bg: "rgba(6,214,160,0.08)",
                    border: "1px solid rgba(6,214,160,0.25)",
                    iconBg: "rgba(6,214,160,0.18)",
                    iconColor: "#06D6A0",
                  }
                : isWarning
                  ? {
                      bg: "rgba(245,158,11,0.08)",
                      border: "1px solid rgba(245,158,11,0.25)",
                      iconBg: "rgba(245,158,11,0.18)",
                      iconColor: "#F59E0B",
                    }
                  : {
                      bg: "rgba(14,165,233,0.08)",
                      border: "1px solid rgba(14,165,233,0.25)",
                      iconBg: "rgba(14,165,233,0.18)",
                      iconColor: "#0EA5E9",
                    };

              return (
                <div
                  key={`${item.title}-${index}`}
                  className="flex gap-3.5 rounded-2xl p-4 transition-all duration-200 hover:-translate-y-0.5 shadow-sm"
                  style={{
                    background: tintStyle.bg,
                    border: tintStyle.border,
                  }}
                >
                  <div
                    className="p-2 rounded-xl shrink-0 self-start mt-0.5 flex items-center justify-center shadow-inner"
                    style={{ background: tintStyle.iconBg, color: tintStyle.iconColor }}
                  >
                    {item.type === "positive" && <CheckCircle2 className="h-4.5 w-4.5" />}
                    {item.type === "warning" && <AlertTriangle className="h-4.5 w-4.5" />}
                    {item.type === "info" && <Activity className="h-4.5 w-4.5" />}
                  </div>
                  <div>
                    <p
                      className="text-sm font-bold tracking-tight"
                      style={{ color: "var(--text-primary)" }}
                    >
                      {item.title}
                    </p>
                    <p
                      className="mt-1 text-xs sm:text-sm leading-relaxed font-medium"
                      style={{ color: "var(--text-secondary)" }}
                    >
                      {item.message}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recommended Next Steps */}
        <div
          className="glass-panel rounded-3xl p-6 sm:p-7 space-y-4 shadow-xl"
          style={{ border: "1px solid var(--border-color)" }}
        >
          <h3
            className="font-extrabold flex items-center gap-2 text-base"
            style={{ color: "var(--text-primary)", fontFamily: "Plus Jakarta Sans, sans-serif" }}
          >
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(6,214,160,0.6)]"></span>
            Recommended Next Steps
          </h3>

          <div className="mt-4 space-y-3">
            {data.recommendations.map((recommendation, index) => (
              <div
                key={index}
                className="flex gap-3.5 rounded-2xl p-4 items-start transition-all duration-200 hover:-translate-y-0.5 shadow-sm"
                style={{
                  background: "var(--bg-surface)",
                  border: "1px solid var(--border-color)",
                }}
              >
                <span
                  className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-black text-white shadow-sm"
                  style={{
                    background: "linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)",
                  }}
                >
                  {index + 1}
                </span>
                <p
                  className="text-xs sm:text-sm leading-relaxed font-medium pt-0.5"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {recommendation}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <p className="px-2 text-xs font-medium italic" style={{ color: "var(--text-muted)" }}>
        * {data.disclaimer}
      </p>
    </section>
  );
}

function MetricCard({
  icon,
  iconBg,
  label,
  value,
  suffix,
}: {
  icon: React.ReactNode;
  iconBg: string;
  label: string;
  value: string;
  suffix: string;
}) {
  return (
    <div
      className="p-4 rounded-2xl transition-all duration-200 hover:-translate-y-0.5 shadow-sm"
      style={{
        background: "var(--bg-surface)",
        border: "1px solid var(--border-color)",
      }}
    >
      <div className="flex items-center gap-2">
        <div
          className="p-1.5 rounded-lg flex items-center justify-center"
          style={{ background: iconBg }}
        >
          {icon}
        </div>
        <span
          className="text-[11px] font-bold uppercase tracking-wider"
          style={{ color: "var(--text-muted)" }}
        >
          {label}
        </span>
      </div>
      <div className="mt-2.5 flex items-baseline">
        <span
          className="text-2xl font-black tracking-tight"
          style={{ color: "var(--text-primary)", fontFamily: "Plus Jakarta Sans, sans-serif" }}
        >
          {value}
        </span>
        <span className="ml-1.5 text-xs font-semibold" style={{ color: "var(--text-muted)" }}>
          {suffix}
        </span>
      </div>
    </div>
  );
}
