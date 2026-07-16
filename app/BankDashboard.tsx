"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Transaction = {
  id: string;
  title: string;
  category: string;
  date: string;
  amount: number;
  icon: string;
};

type ApiAccount = {
  id: string;
  account_number: string;
  account_type: string;
  currency: string;
  balance_cents: number;
};

type ApiTransfer = {
  id: string;
  source_account_id: string;
  amount_cents: number;
  description: string;
  created_at: string;
};

const seedTransactions: Transaction[] = [
  { id: "TXN-84291", title: "Acme Payroll", category: "Income", date: "Today, 9:41 AM", amount: 4850, icon: "AP" },
  { id: "TXN-84274", title: "AWS Cloud Services", category: "Infrastructure", date: "Yesterday, 4:18 PM", amount: -186.42, icon: "AWS" },
  { id: "TXN-84212", title: "Whole Foods Market", category: "Groceries", date: "Jul 12, 6:32 PM", amount: -92.18, icon: "WF" },
  { id: "TXN-84196", title: "Monthly savings", category: "Transfer", date: "Jul 11, 8:00 AM", amount: -1000, icon: "NS" },
];

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

export function BankDashboard() {
  const [balance, setBalance] = useState(24782.64);
  const [transactions, setTransactions] = useState(seedTransactions);
  const [showTransfer, setShowTransfer] = useState(false);
  const [notice, setNotice] = useState("");
  const [filter, setFilter] = useState("");
  const [accounts, setAccounts] = useState<ApiAccount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const accountResponse = await fetch("/api/accounts", { cache: "no-store" });
        if (!accountResponse.ok) throw new Error("Account service unavailable");
        const loadedAccounts = (await accountResponse.json()) as ApiAccount[];
        setAccounts(loadedAccounts);
        const checking = loadedAccounts.find((account) => account.account_type === "checking");
        if (!checking) throw new Error("No checking account found");
        setBalance(checking.balance_cents / 100);
        const transferResponse = await fetch(`/api/transfers?account_id=${checking.id}`);
        if (transferResponse.ok) {
          const loaded = (await transferResponse.json()) as ApiTransfer[];
          setTransactions(loaded.map((transfer) => ({
            id: transfer.id.slice(0, 13).toUpperCase(),
            title: transfer.description,
            category: "Transfer",
            date: new Date(transfer.created_at).toLocaleString(),
            amount: transfer.source_account_id === checking.id ? -(transfer.amount_cents / 100) : transfer.amount_cents / 100,
            icon: "NS",
          })));
        }
      } catch {
        setNotice("Live banking data is unavailable. Displaying synthetic preview data.");
      } finally {
        setLoading(false);
      }
    }
    void loadDashboard();
  }, []);

  const filtered = useMemo(
    () => transactions.filter((item) => `${item.title} ${item.category} ${item.id}`.toLowerCase().includes(filter.toLowerCase())),
    [filter, transactions],
  );

  async function submitTransfer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const destinationAccountId = String(data.get("destination_account_id") || "").trim();
    const amount = Number(data.get("amount"));
    const source = accounts.find((account) => account.account_type === "checking");
    if (!source || !destinationAccountId || !Number.isFinite(amount) || amount <= 0) return;
    const response = await fetch("/api/transfers", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Idempotency-Key": crypto.randomUUID() },
      body: JSON.stringify({
        source_account_id: source.id,
        destination_account_id: destinationAccountId,
        amount,
        currency: source.currency,
        description: "Northstar account transfer",
      }),
    });
    if (!response.ok) {
      const error = (await response.json()) as { detail?: string; error?: string };
      setNotice(error.detail ?? error.error ?? "Transfer could not be completed.");
      return;
    }
    setBalance((value) => value - amount);
    setTransactions((items) => [{
      id: `TXN-${Date.now().toString().slice(-5)}`,
      title: "Northstar account transfer",
      category: "Transfer",
      date: "Just now",
      amount: -amount,
      icon: "NS",
    }, ...items]);
    setShowTransfer(false);
    setNotice(`${money.format(amount)} transfer completed.`);
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <a className="brand" href="#top" aria-label="Northstar Bank home"><span className="brand-mark">N</span><span>Northstar <b>Bank</b></span></a>
        <nav aria-label="Primary navigation">
          <a className="active" href="#top"><span>⌂</span> Overview</a>
          <a href="#accounts"><span>▣</span> Accounts</a>
          <a href="#transactions"><span>⇄</span> Transactions</a>
          <a href="#cards"><span>▭</span> Cards</a>
          <a href="#insights"><span>◫</span> Insights</a>
        </nav>
        <div className="sidebar-bottom">
          <a href="#support"><span>?</span> Support</a>
          <a href="#settings"><span>⚙</span> Settings</a>
          <div className="profile"><span className="avatar">JG</span><span><b>Grace Johnson</b><small>Personal account</small></span><button aria-label="Open profile menu">•••</button></div>
        </div>
      </aside>

      <section className="content" id="top">
        <header className="topbar">
          <div><p className="eyebrow">Tuesday, July 14</p><h1>Good evening, Grace.</h1></div>
          <div className="top-actions"><button className="icon-button" aria-label="Notifications">♢<i /></button><button className="primary" onClick={() => setShowTransfer(true)}>＋ Send money</button></div>
        </header>

        {notice && <div className="notice" role="status"><span>✓</span>{notice}<button onClick={() => setNotice("")} aria-label="Dismiss">×</button></div>}

        <div className="dashboard-grid">
          <section className="balance-card" id="accounts">
            <div className="balance-head"><span>PRIMARY CHECKING</span><button aria-label="Account options">•••</button></div>
            <p className="account-number">•••• 4821</p>
            <p className="balance-label">{loading ? "Loading live balance…" : "Available balance"}</p>
            <p className="balance">{money.format(balance)}</p>
            <div className="balance-meta"><span><small>Current balance</small><b>{money.format(balance + 318.4)}</b></span><span><small>Pending</small><b>{money.format(318.4)}</b></span></div>
            <div className="balance-actions"><button onClick={() => setShowTransfer(true)}>⇧<span>Transfer</span></button><button>＋<span>Deposit</span></button><button>▦<span>Pay bill</span></button><button>•••<span>More</span></button></div>
          </section>

          <section className="snapshot" id="insights">
            <div className="section-heading"><div><p className="eyebrow">FINANCIAL SNAPSHOT</p><h2>July overview</h2></div><button>Last 30 days⌄</button></div>
            <div className="snapshot-values"><div><small>Money in</small><b className="positive">{money.format(6240)}</b><em>↑ 8.2%</em></div><div><small>Money out</small><b>{money.format(3891.54)}</b><em className="neutral">↓ 2.4%</em></div></div>
            <div className="chart" aria-label="Income and spending chart"><span style={{height:"38%"}}/><span style={{height:"51%"}}/><span style={{height:"42%"}}/><span style={{height:"69%"}}/><span style={{height:"48%"}}/><span style={{height:"79%"}}/><span className="today" style={{height:"62%"}}/></div>
            <div className="chart-labels"><span>Jun 15</span><span>Jun 22</span><span>Jun 29</span><span>Jul 6</span><span>Today</span></div>
          </section>

          <section className="transactions" id="transactions">
            <div className="section-heading"><div><p className="eyebrow">ACTIVITY</p><h2>Recent transactions</h2></div><a href="#transactions">View all →</a></div>
            <label className="search"><span>⌕</span><input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Search transactions" /></label>
            <div className="transaction-list">
              {filtered.map((item) => <article key={item.id}><span className="merchant">{item.icon}</span><span className="transaction-name"><b>{item.title}</b><small>{item.category} · {item.id}</small></span><span className="transaction-date">{item.date}</span><b className={item.amount > 0 ? "credit" : ""}>{item.amount > 0 ? "+" : "−"}{money.format(Math.abs(item.amount))}</b></article>)}
              {!filtered.length && <p className="empty">No matching transactions.</p>}
            </div>
          </section>

          <aside className="side-stack">
            <section className="savings"><div className="section-heading"><div><p className="eyebrow">SAVINGS GOAL</p><h2>Emergency fund</h2></div><span>68%</span></div><div className="progress"><i /></div><p><b>{money.format(6800)}</b> of {money.format(10000)}</p><small>At this pace, you’ll reach your goal by October.</small><button>＋ Add money</button></section>
            <section className="system"><div><span className="pulse"/><b>All systems operational</b></div><small>Services checked 1 minute ago</small><a href="#system">View service health →</a></section>
          </aside>
        </div>
      </section>

      {showTransfer && <div className="modal-backdrop" role="presentation" onMouseDown={() => setShowTransfer(false)}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="transfer-title" onMouseDown={(e) => e.stopPropagation()}><button className="close" onClick={() => setShowTransfer(false)} aria-label="Close">×</button><p className="eyebrow">SECURE TRANSFER</p><h2 id="transfer-title">Send money</h2><p>Move funds from your primary checking account.</p><form onSubmit={submitTransfer}><label>Destination account<select name="destination_account_id" required autoFocus><option value="">Choose an account</option>{accounts.filter((account) => account.account_type !== "checking").map((account) => <option key={account.id} value={account.id}>{account.account_type} · •••• {account.account_number.slice(-4)}</option>)}</select></label><label>Amount<div className="amount-input"><span>$</span><input name="amount" required type="number" min="0.01" max={balance} step="0.01" placeholder="0.00" /></div></label><small>Available: {money.format(balance)}</small><button className="primary" type="submit">Review transfer →</button></form></section></div>}
    </main>
  );
}
