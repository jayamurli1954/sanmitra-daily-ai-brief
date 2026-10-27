import React from "react";
import { AbsoluteFill } from "remotion";
import { BarLineChart, DivergingLines, PALETTE, Waterfall } from "../charts";
import { At, Chip, EndCard, Episode, episodeFrames, OfficeMitraMoment, RIGHT, Scene, SceneArt } from "../episode";
import {
  Boxes,
  BigLines,
  FONT,
  ForecastBars,
  GrowthLoop,
  InvoiceTimeline,
  ItemList,
  MiniSheet,
  PairedBars,
  Panel,
  SplitCompare,
  TrendLine,
  usePop,
} from "../graphics";
import timingsData from "./timings.json";

/**
 * OfficeMitra Finance Insights, Episode 001: "Profit is Vanity, Cash is Reality".
 * Story and figures from newsletter Issue #1; the month-by-month series, the
 * 8-week forecast and the characters are illustrative (see
 * out/finance/pilot_001_script_storyboard.md for the checked numbers).
 * Pictures: Gemini stills and clips in public/finance/ramesh/.
 */

const SCENES = (timingsData as { scenes: Scene[] }).scenes;
export { EP_FPS } from "../episode";
export const pilotFrames = () => episodeFrames(SCENES);

const MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"];

// Scene id -> picture + graphic. `len` is the scene length in frames.
const SCENE_ART: SceneArt = {
  s01: {
    shot: { kind: "still", src: "shot2_celebrate.png", zoom: [1.0, 1.1], origin: "25% 35%" },
    graphic: () => (
      <>
        <At {...RIGHT}>
          <Panel title="Sales and profit" tag="₹ LAKH · ILLUSTRATIVE" enter={usePop(15)} width={800}>
            <BarLineChart labels={MONTHS} bars={[32, 36, 38, 41, 45, 50]} line={[5, 6, 6.5, 7, 8, 10]} max={60} start={40} barLabel="Sales" lineLabel="Profit" width={730} height={380} />
          </Panel>
        </At>
        <Chip at={210} color={PALETTE.green} left={1100} top={640}>★ Best month ever</Chip>
      </>
    ),
  },
  s02: {
    shot: { kind: "clip", src: "c02_celebration.mp4", seconds: 10, still: "s02_celebration.png" },
    graphic: () => (
      <At left={70} top={60}>
        <Panel enter={usePop(40)} width={520}>
          <div style={{ fontSize: 22, fontWeight: 700, color: PALETTE.muted, letterSpacing: 2 }}>NEW ORDER</div>
          <div style={{ fontSize: 40, fontWeight: 900 }}>Mehta Traders</div>
          <div style={{ fontSize: 64, fontWeight: 900, color: PALETTE.green }}>₹15 lakh</div>
        </Panel>
      </At>
    ),
  },
  s03: { shot: { kind: "still", src: "s03_lata_door.png", zoom: [1.0, 1.08], origin: "70% 45%" } },
  s04: {
    shot: { kind: "clip", src: "c04_lata_tablet.mp4", seconds: 10, still: "s04_lata_tablet.png" },
    graphic: () => (
      <>
        <At left={60} top={50}>
          <Panel enter={usePop(70)} width={700}>
            <div style={{ fontSize: 22, fontWeight: 800, color: PALETTE.muted, letterSpacing: 2 }}>ACTUALLY COLLECTED</div>
            <div style={{ fontSize: 96, fontWeight: 900, color: PALETTE.red, lineHeight: 1.05 }}>
              ₹5 lakh <span style={{ fontSize: 34, color: PALETTE.muted, fontWeight: 700 }}>of ₹50 lakh</span>
            </div>
          </Panel>
        </At>
        <Chip at={20} color={PALETTE.red} left={70} top={280}>📅 Salaries due on Friday</Chip>
      </>
    ),
  },
  s05: {
    shot: { kind: "stage" },
    graphic: () => (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <BigLines size={110} lines={[{ text: "Profit is Vanity.", color: "#fff", at: 5 }, { text: "Cash is Reality.", color: PALETTE.orange, at: 50 }]} />
        <div style={{ marginTop: 40, color: "rgba(255,255,255,0.7)", fontSize: 30, fontWeight: 700, letterSpacing: 4, fontFamily: FONT }}>
          OFFICEMITRA FINANCE INSIGHTS · EPISODE 1
        </div>
      </AbsoluteFill>
    ),
  },
  s06: {
    shot: { kind: "still", src: "shot1_happy_laptop.png", zoom: [1.0, 1.06], origin: "20% 40%" },
    graphic: () => (
      <At {...RIGHT}>
        <Panel title="Profit and cash arrive at different times" enter={usePop(60)} width={800}>
          <InvoiceTimeline start={190} />
        </Panel>
      </At>
    ),
  },
  s07: {
    shot: { kind: "clip", src: "clip3_phone.mp4", seconds: 9.9, still: "shot3_phone.png" },
    graphic: () => (
      <At {...RIGHT}>
        <Panel title="This month" tag="₹ LAKH" enter={usePop(10)} width={800}>
          <Waterfall
            max={55}
            start={60}
            width={730}
            height={400}
            steps={[
              { label: "Sales", value: 50, kind: "total", color: PALETTE.navy, caption: "invoiced" },
              { label: "With customers", value: 45, kind: "minus", color: PALETTE.orange, caption: "not yet paid" },
              { label: "Collected", value: 5, kind: "result", color: PALETTE.green, caption: "cash in hand" },
            ]}
          />
          <div style={{ fontSize: 24, color: PALETTE.muted, fontWeight: 700 }}>Profit this month: ₹10 lakh</div>
        </Panel>
      </At>
    ),
  },
  s08: {
    shot: { kind: "still", src: "shot4_worried.png", zoom: [1.02, 1.12], origin: "28% 35%" },
    graphic: () => (
      <At left={1120} top={120}>
        <Panel title="These don't wait" enter={usePop(5)} width={680}>
          <ItemList
            items={[
              { icon: "👥", text: "Salaries", at: 20, color: PALETTE.red },
              { icon: "🚚", text: "Suppliers", at: 45, color: PALETTE.red },
              { icon: "🏢", text: "Rent", at: 70, color: PALETTE.orange },
              { icon: "🧾", text: "GST", at: 95, color: PALETTE.orange },
              { icon: "🏦", text: "Loan instalments", at: 120, color: PALETTE.orange },
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s09: {
    shot: { kind: "still", src: "shot5_invoices.png", zoom: [1.04, 1.08] },
    dim: 0.72,
    graphic: () => (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: 40, fontFamily: FONT }}>
        <div style={{ color: "#fff", fontSize: 64, fontWeight: 900 }}>Where the cash gets stuck</div>
        <Boxes
          width={330}
          items={[
            { title: "1. Collections", sub: "customers pay late", color: PALETTE.red, at: 15 },
            { title: "2. Inventory", sub: "cash on shelves", color: PALETTE.orange, at: 35 },
            { title: "3. Growth", sub: "paid for first", color: PALETTE.green, at: 55 },
            { title: "4. Capital spend", sub: "cash out on day one", color: PALETTE.navy, at: 75 },
          ]}
        />
      </AbsoluteFill>
    ),
  },
  s10: {
    shot: { kind: "still", src: "s10_mehta_phone.png", zoom: [1.0, 1.08], origin: "25% 40%" },
    graphic: () => (
      <At {...RIGHT}>
        <Panel title="Debtor days creeping up" tag="ILLUSTRATIVE" enter={usePop(250)} width={800}>
          <TrendLine labels={["Apr", "Jun", "Jul", "Aug", "Sep"]} values={[45, 52, 58, 66, 72]} max={80} start={280} color={PALETTE.red} unit="d" />
        </Panel>
      </At>
    ),
  },
  s11: {
    shot: { kind: "still", src: "s11_godown.png", zoom: [1.0, 1.1], origin: "30% 50%" },
    graphic: () => (
      <At {...RIGHT}>
        <Panel title="Stock is rising faster than sales" tag="₹ LAKH · ILLUSTRATIVE" enter={usePop(60)} width={800}>
          <PairedBars labels={MONTHS} a={[30, 33, 37, 41, 45, 48]} b={[45, 46, 47, 48, 49, 50]} aLabel="Stock on hand" bLabel="Monthly sales" max={60} start={90} />
        </Panel>
      </At>
    ),
  },
  s12: {
    shot: { kind: "still", src: "s12_vikram_pitch.png", zoom: [1.0, 1.06], origin: "40% 40%" },
    graphic: () => (
      <At left={1300} top={70}>
        <Panel enter={usePop(250)} width={580} padding="18px 20px">
          <GrowthLoop start={270} />
        </Panel>
      </At>
    ),
  },
  s13: {
    shot: { kind: "still", src: "s13_van.png", zoom: [1.0, 1.06], origin: "35% 50%" },
    graphic: () => (
      <At left={1000} top={130}>
        <Panel title="The ₹20 lakh delivery van" enter={usePop(90)} width={860}>
          <SplitCompare start={200} left={{ label: "Bank, day one", value: "−₹20L", color: PALETTE.red }} right={{ label: "P&L, per year", value: "₹2L", color: PALETTE.green }} />
          <div style={{ fontSize: 22, color: PALETTE.muted, marginTop: 12 }}>Depreciation over about 10 years</div>
        </Panel>
      </At>
    ),
  },
  s14: {
    shot: { kind: "still", src: "s14_lata_desk.png", zoom: [1.0, 1.08], origin: "25% 40%" },
    graphic: () => (
      <At left={1080} top={110}>
        <Panel title="Lata's warning signs" enter={usePop(100)} width={760}>
          <ItemList
            size={28}
            items={[
              { icon: "⚠️", text: "Debtor days creeping up", at: 170, color: PALETTE.red },
              { icon: "⚠️", text: "Stock rising faster than sales", at: 230, color: PALETTE.red },
              { icon: "⚠️", text: "Overdraft used more often", at: 300, color: PALETTE.red },
              { icon: "⚠️", text: "Supplier payments pushed back", at: 370, color: PALETTE.red },
              { icon: "⚠️", text: "Bank balance falling", at: 470, color: PALETTE.red },
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s15: {
    shot: { kind: "split", left: "s15_kapoor_call.png", right: "shot4_worried.png" },
    graphic: () => <Chip at={40} color={PALETTE.red} left={700} top={70}>⏱ 90 days overdue</Chip>,
  },
  s16: {
    shot: { kind: "still", src: "shot3_phone.png", zoom: [1.02, 1.1], origin: "25% 40%" },
    graphic: () => (
      <At {...RIGHT}>
        <Panel title="Profit vs bank balance" tag="₹ LAKH · ILLUSTRATIVE" enter={usePop(20)} width={800}>
          <DivergingLines labels={MONTHS} up={[5, 6, 6.5, 7, 8, 10]} down={[30, 26, 20, 14, 9, 5]} max={32} start={50} upLabel="Profit" downLabel="Bank" width={740} height={400} />
        </Panel>
      </At>
    ),
  },
  s17: {
    shot: { kind: "stillThenClip", still: "s17_forecast.png", clip: "c17_forecast.mp4", clipSeconds: 8 },
    graphic: () => (
      <At left={1390} top={24}>
        <Panel title="8-week cash forecast" tag="₹ LAKH" enter={usePop(160)} width={500} padding="14px 20px">
          <ForecastBars closing={[0, -2, -4, -2, -1, 3, 7, 12]} start={190} highlight={2} width={450} height={230} />
        </Panel>
      </At>
    ),
  },
  s18: {
    shot: { kind: "still", src: "s18_ramesh_call.png", zoom: [1.0, 1.06], origin: "45% 40%" },
    graphic: () => (
      <At left={1330} top={140}>
        <Panel title="Act early" enter={usePop(140)} width={560}>
          <ItemList
            size={26}
            items={[
              { icon: "📞", text: "Call 3 overdue customers", at: 190, color: PALETTE.green },
              { icon: "🤝", text: "Agree supplier dates", at: 300, color: PALETTE.green },
              { icon: "🏦", text: "Arrange the bank limit now", at: 420, color: PALETTE.green },
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s19: {
    shot: { kind: "still", src: "s14_lata_desk.png", zoom: [1.08, 1.0], origin: "30% 45%" },
    graphic: () => (
      <At left={1080} top={150}>
        <Panel title="Every Monday" enter={usePop(10)} width={760}>
          <MiniSheet
            start={30}
            rows={[
              ["W1", 4, 9, 0],
              ["W2", 6, 8, -2],
              ["W3", 5, 7, -4],
              ["W4", 8, 6, -2],
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s20: {
    shot: { kind: "stage" },
    graphic: () => (
      <OfficeMitraMoment
        screen="cfo-02-cash-forecast.png"
        caption="OfficeMitra · CFO pack · Cash forecast"
        points={["Read-only: never changes your books", "Tally · Zoho · any ERP export", "Runs on your own computer", "30 / 60 / 90-day cash forecast"]}
      />
    ),
  },
  s21: {
    shot: { kind: "clip", src: "c21_calm_evening.mp4", seconds: 10, still: "s21_calm_evening.png" },
    graphic: () => (
      <At left={0} top={50}>
        <div style={{ width: 1920 }}>
          <Boxes
            width={640}
            items={[
              { title: "Profit asks", sub: "Did the business create value?", color: PALETTE.green, at: 90 },
              { title: "Cash asks", sub: "Can it keep operating tomorrow?", color: PALETTE.orange, at: 200 },
            ]}
          />
        </div>
      </At>
    ),
  },
  s22: {
    shot: { kind: "still", src: "s21_calm_evening.png", zoom: [1.04, 1.1] },
    dim: 0.7,
    graphic: (len) => (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <BigLines
          size={88}
          lines={[
            { text: "Profit measures performance.", color: "#fff", at: Math.round(len * 0.55) },
            { text: "Cash determines survival.", color: PALETTE.orange, at: Math.round(len * 0.7) },
          ]}
        />
      </AbsoluteFill>
    ),
  },
  s23: {
    shot: { kind: "still", src: "shot1_happy_laptop.png", zoom: [1.06, 1.0], origin: "25% 40%" },
    graphic: () => (
      <At left={1080} top={120}>
        <Panel title="Try this this week" enter={usePop(10)} width={760}>
          <ItemList
            size={28}
            items={[
              { icon: "1️⃣", text: "Last month's profit", at: 140, color: PALETTE.green },
              { icon: "2️⃣", text: "Change in bank balance", at: 200, color: PALETTE.navy },
              { icon: "3️⃣", text: "Change in debtors + stock", at: 280, color: PALETTE.orange },
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s24: {
    shot: { kind: "stage" },
    graphic: () => <EndCard question="Which number do you check first?" />,
  },
};

export const Pilot001: React.FC = () => <Episode scenes={SCENES} art={SCENE_ART} />;
