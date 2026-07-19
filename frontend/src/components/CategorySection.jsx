import GradedFieldCard from "./GradedFieldCard";

export default function CategorySection({ id, title, fields }) {
  return (
    <section id={id} className="scroll-mt-24">
      <h2 className="font-display text-xl text-ink">{title}</h2>
      <div
        className={`mt-3 grid gap-3 ${
          fields.length > 1 ? "sm:grid-cols-2 lg:grid-cols-3" : "grid-cols-1"
        }`}
      >
        {fields.map(({ label, field }) => (
          <GradedFieldCard key={label} label={label} field={field} />
        ))}
      </div>
    </section>
  );
}
