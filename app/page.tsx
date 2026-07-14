import type { Metadata } from "next";
import { BankDashboard } from "./BankDashboard";

export const metadata: Metadata = {
  title: "Overview",
  description: "A production-minded banking platform built for DevOps practice.",
};

export default function Home() {
  return <BankDashboard />;
}
