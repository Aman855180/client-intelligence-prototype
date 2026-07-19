import CategorySection from "./CategorySection";
import GradedFieldCard from "./GradedFieldCard";
import FindingCard from "./FindingCard";

function ListSection({ id, title, items, emptyLabel, renderItem }) {
  return (
    <section id={id} className="scroll-mt-24">
      <h2 className="font-display text-xl text-ink">{title}</h2>
      {items && items.length > 0 ? (
        <div className="mt-3 grid gap-3 sm:grid-cols-2">{items.map(renderItem)}</div>
      ) : (
        <p className="mt-3 text-sm text-faint italic">Nothing reported in this category.</p>
      )}
    </section>
  );
}

export default function ReportBody({ report }) {
  const {
    nutrition,
    exercise,
    sleep,
    water,
    symptoms,
    stress,
    engagement,
    key_barriers: barriers,
    risk_flags: riskFlags,
    coach_recommendations: recommendations,
    conflicting_reports: conflicts,
    missing_information: missing,
  } = report;

  return (
    <div className="mx-auto max-w-5xl space-y-10 px-6 py-10">
      <CategorySection
        id="nutrition"
        title="Nutrition"
        fields={[
          { label: "Adherence", field: nutrition.adherence },
          { label: "Notes", field: nutrition.notes },
        ]}
      />

      <CategorySection
        id="exercise"
        title="Exercise"
        fields={[
          { label: "Steps", field: exercise.steps },
          { label: "Activity Type", field: exercise.activity_type },
          { label: "Consistency", field: exercise.consistency },
        ]}
      />

      <CategorySection
        id="sleep"
        title="Sleep"
        fields={[
          { label: "Average Hours", field: sleep.average_hours },
          { label: "Quality Notes", field: sleep.quality_notes },
        ]}
      />

      <section id="water" className="scroll-mt-24">
        <h2 className="font-display text-xl text-ink">Water</h2>
        <div className="mt-3 max-w-md">
          <GradedFieldCard label="Water Intake" field={water} />
        </div>
      </section>

      <CategorySection
        id="symptoms"
        title="Symptoms"
        fields={[
          { label: "Reported Symptoms", field: symptoms.reported_symptoms },
          { label: "Frequency Pattern", field: symptoms.frequency_pattern },
        ]}
      />

      <section id="stress" className="scroll-mt-24">
        <h2 className="font-display text-xl text-ink">Stress</h2>
        <div className="mt-3 max-w-md">
          <GradedFieldCard label="Stress Indicators" field={stress} />
        </div>
      </section>

      <CategorySection
        id="engagement"
        title="Engagement"
        fields={[
          { label: "Level", field: engagement.level },
          { label: "Responsiveness", field: engagement.responsiveness },
          { label: "Missed Check-ins", field: engagement.missed_checkins },
        ]}
      />

      <ListSection
        id="barriers"
        title="Key Barriers"
        items={barriers}
        renderItem={(item, i) => (
          <FindingCard
            key={i}
            text={item.description}
            classification={item.classification}
            confidence={item.confidence}
            evidence={item.evidence}
          />
        )}
      />

      <ListSection
        id="risks"
        title="Risk Flags"
        items={riskFlags}
        renderItem={(item, i) => (
          <FindingCard
            key={i}
            text={item.flag}
            classification={item.classification}
            confidence={item.confidence}
            evidence={item.evidence}
            tag={{ label: `${item.severity} severity`, toneKey: item.severity }}
            meta={item.rule_triggered}
          />
        )}
      />

      <ListSection
        id="recommendations"
        title="Coach Recommendations"
        items={recommendations}
        renderItem={(item, i) => (
          <FindingCard
            key={i}
            text={item.recommendation}
            classification={item.classification}
            confidence={item.confidence}
            evidence={item.evidence}
            tag={{ label: `${item.priority} priority`, toneKey: item.priority }}
          />
        )}
      />

      {conflicts && conflicts.length > 0 && (
        <ListSection
          id="conflicts"
          title="Conflicting Reports"
          items={conflicts}
          renderItem={(item, i) => (
            <FindingCard
              key={i}
              text={item.description}
              classification={item.classification}
              confidence={1}
              evidence={item.evidence}
            />
          )}
        />
      )}

      {missing && missing.length > 0 && (
        <section id="missing" className="scroll-mt-24">
          <h2 className="font-display text-xl text-ink">Missing Information</h2>
          <div className="mt-3 rounded-lg border border-missing/30 bg-missing-soft p-4">
            <ul className="space-y-1.5">
              {missing.map((item, i) => (
                <li key={i} className="text-sm text-ink">
                  <span className="font-medium">{item.category}:</span>{" "}
                  <span className="text-muted">{item.note}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}
    </div>
  );
}
