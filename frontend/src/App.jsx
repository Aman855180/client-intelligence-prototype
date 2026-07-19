import { useState } from "react";
import { analyzeConversation } from "./api/analyzeClient";
import TranscriptInputPanel from "./components/TranscriptInputPanel";
import ReportHeader from "./components/ReportHeader";
import ReportBody from "./components/ReportBody";
import ReviewActionBar from "./components/ReviewActionBar";
import sampleReport from "./data/sampleReport.json";

export default function App() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [reviewStatus, setReviewStatus] = useState("pending");

  const handleSubmit = async (conversation) => {
    setLoading(true);
    setError("");
    try {
      const data = await analyzeConversation(conversation);
      setReport(data);
      setReviewStatus("pending");
    } catch (err) {
      setError(err.message || "Something went wrong while analyzing the conversation.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setReport(null);
    setError("");
    setReviewStatus("pending");
  };

  const handleViewSample = () => {
    setError("");
    setReport(sampleReport);
    setReviewStatus("pending");
  };

  if (!report) {
    return (
      <div className="min-h-screen bg-bg">
        <TranscriptInputPanel
          onSubmit={handleSubmit}
          loading={loading}
          error={error}
          onViewSample={handleViewSample}
        />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-bg">
      <ReportHeader report={report} onReset={handleReset} />
      <main className="flex-1">
        <ReportBody report={report} />
      </main>
      <ReviewActionBar
        status={reviewStatus}
        onApprove={() => setReviewStatus("approved")}
        onEdit={() => setReviewStatus("edited")}
        onReject={() => setReviewStatus("rejected")}
      />
    </div>
  );
}
