import { Filter } from "lucide-react";

export interface QuestionFilterValues {
  difficulty: string;
  question_type: string;
  order: "asc" | "desc";
}

interface QuestionFiltersProps {
  filters: QuestionFilterValues;
  onChange: (filters: QuestionFilterValues) => void;
}

export function QuestionFilters({ filters, onChange }: QuestionFiltersProps) {
  const handleDifficultyChange = (e: { target: { value: string } }) => {
    onChange({ ...filters, difficulty: e.target.value });
  };

  const handleTypeChange = (e: { target: { value: string } }) => {
    onChange({ ...filters, question_type: e.target.value });
  };

  const handleOrderChange = (e: { target: { value: string } }) => {
    onChange({ ...filters, order: e.target.value as "asc" | "desc" });
  };

  return (
    <section className="panel question-filters">
      <div className="panel-header" style={{ marginBottom: 12 }}>
        <h2 className="panel-title" style={{ fontSize: "0.9rem", display: "flex", alignItems: "center", gap: 6 }}>
          <Filter size={14} />
          Filters
        </h2>
      </div>
      <div className="filter-row">
        <label className="filter-label">
          Difficulty
          <select value={filters.difficulty} onChange={handleDifficultyChange} className="filter-select">
            <option value="">All</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </label>

        <label className="filter-label">
          Type
          <select value={filters.question_type} onChange={handleTypeChange} className="filter-select">
            <option value="">All</option>
            <option value="mcq">Multiple Choice</option>
            <option value="true_false">True / False</option>
            <option value="short_answer">Short Answer</option>
          </select>
        </label>

        <label className="filter-label">
          Order
          <select value={filters.order} onChange={handleOrderChange} className="filter-select">
            <option value="asc">Oldest first</option>
            <option value="desc">Newest first</option>
          </select>
        </label>
      </div>
    </section>
  );
}
