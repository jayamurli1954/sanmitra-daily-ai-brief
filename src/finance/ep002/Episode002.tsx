import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { PALETTE, Waterfall } from "../charts";
import { At, Chip, cueFor, EndCard, Episode, episodeFrames, OfficeMitraMoment, RIGHT, Scene, SceneArt } from "../episode";
import { BigLines, Boxes, CycleLoop, FONT, GapBridge, ItemList, Panel, RupeeTimeline, SplitCompare, usePop } from "../graphics";
import timingsData from "./timings.json";

/**
 * OfficeMitra Finance Insights, Episode 002: "Working Capital: The Investment Most
 * SMEs Don't Realise They're Making". Story from newsletter Issue #2; Sharma Retail,
 * the ₹20 lakh order and every figure are illustrative (checked in
 * out/finance/ep002_script_storyboard.md). Pictures are EP001's, plus the bank scene.
 * Graphics are timed to the narration with `cue(scene, line, fraction of the line)`.
 */

const SCENES = (timingsData as { scenes: Scene[] }).scenes;
export const episode002Frames = () => episodeFrames(SCENES);
const cue = cueFor(SCENES);

const TitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const second = cue("s05", 1);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", fontFamily: FONT }}>
      {frame < second - 6 ? (
        <BigLines
          size={96}
          lines={[
            { text: "₹40 lakh.", color: PALETTE.orange, at: 5 },
            { text: "Not for a godown. Not for a van.", color: "#fff", at: cue("s05", 0, 0.2) },
            { text: "Just to keep running.", color: "#fff", at: cue("s05", 0, 0.7) },
          ]}
        />
      ) : (
        <>
          <BigLines size={120} lines={[{ text: "Working Capital", color: "#fff", at: second }]} />
          <div style={{ marginTop: 20 }}>
            <BigLines size={50} lines={[{ text: "The investment most SMEs don't realise they're making", color: PALETTE.orange, at: second + 25 }]} />
          </div>
          <div style={{ marginTop: 40, color: "rgba(255,255,255,0.7)", fontSize: 30, fontWeight: 700, letterSpacing: 4 }}>OFFICEMITRA FINANCE INSIGHTS · EPISODE 2</div>
        </>
      )}
    </AbsoluteFill>
  );
};

const SCENE_ART: SceneArt = {
  s01: {
    shot: { kind: "still", src: "shot4_worried.png", zoom: [1.02, 1.1], origin: "28% 35%", gray: 0.85 },
    graphic: () => (
      <>
        <Chip at={8} color={PALETTE.navy} left={70} top={60}>⏪ Six months ago</Chip>
        <At {...RIGHT}>
          <Panel enter={usePop(cue("s01", 0, 0.35))} width={700}>
            <div style={{ fontSize: 22, fontWeight: 800, color: PALETTE.muted, letterSpacing: 2 }}>EPISODE 1 · BEST MONTH EVER</div>
            <div style={{ fontSize: 80, fontWeight: 900, color: PALETTE.red, lineHeight: 1.05 }}>
              ₹5 lakh <span style={{ fontSize: 32, color: PALETTE.muted, fontWeight: 700 }}>collected of ₹50 lakh</span>
            </div>
          </Panel>
        </At>
      </>
    ),
  },
  s02: {
    shot: { kind: "clip", src: "c02_celebration.mp4", seconds: 10, still: "s02_celebration.png" },
    graphic: () => (
      <At left={70} top={60}>
        <Panel enter={usePop(cue("s02", 0, 0.35))} width={560}>
          <div style={{ fontSize: 22, fontWeight: 700, color: PALETTE.muted, letterSpacing: 2 }}>NEW CUSTOMER</div>
          <div style={{ fontSize: 40, fontWeight: 900 }}>Sharma Retail</div>
          <div style={{ fontSize: 60, fontWeight: 900, color: PALETTE.green }}>
            ₹20 lakh <span style={{ fontSize: 30, color: PALETTE.muted }}>every month</span>
          </div>
        </Panel>
      </At>
    ),
  },
  s03: { shot: { kind: "still", src: "s03_lata_door.png", zoom: [1.0, 1.08], origin: "70% 45%" } },
  s04: {
    shot: { kind: "clip", src: "c04_lata_tablet.mp4", seconds: 10, still: "s04_lata_tablet.png" },
    graphic: () => (
      <At left={60} top={50}>
        <Panel enter={usePop(cue("s04", 0, 0.15))} width={760}>
          <SplitCompare
            start={cue("s04", 0, 0.85) - 70}
            left={{ label: "Earns, per month", value: "~₹5L", color: PALETTE.green }}
            right={{ label: "Needs first", value: "₹40L", color: PALETTE.red }}
          />
        </Panel>
      </At>
    ),
  },
  s05: { shot: { kind: "stage" }, graphic: () => <TitleCard /> },
  s06: {
    shot: { kind: "still", src: "s13_van.png", zoom: [1.0, 1.06], origin: "35% 50%" },
    graphic: () => (
      <At left={1100} top={130}>
        <Panel title="Investments you can see" enter={usePop(cue("s06", 0, 0.3))} width={720}>
          <ItemList
            items={[
              { icon: "🏭", text: "A new machine", at: cue("s06", 0, 0.62), color: PALETTE.navy },
              { icon: "🚚", text: "A delivery vehicle", at: cue("s06", 0, 0.76), color: PALETTE.navy },
              { icon: "🏢", text: "An office renovation", at: cue("s06", 0, 0.88), color: PALETTE.navy },
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s07: {
    shot: { kind: "still", src: "shot1_happy_laptop.png", zoom: [1.0, 1.06], origin: "20% 40%" },
    graphic: () => (
      <At {...RIGHT}>
        <Panel title="Working capital" tag="THE INVISIBLE ONE" enter={usePop(cue("s07", 0, 0.05))} width={760}>
          <div style={{ border: `4px dashed ${PALETTE.grid}`, borderRadius: 16, padding: 18 }}>
            <ItemList
              size={30}
              items={[
                { icon: "👁️", text: "You don't see it", at: cue("s07", 0, 0.25), color: PALETTE.orange },
                { icon: "✂️", text: "No ribbon to cut", at: cue("s07", 0, 0.5), color: PALETTE.orange },
                { icon: "📣", text: "No announcement", at: cue("s07", 0, 0.75), color: PALETTE.orange },
                { icon: "📅", text: "Invested every single day", at: cue("s07", 1, 0.3), color: PALETTE.red },
              ]}
            />
          </div>
        </Panel>
      </At>
    ),
  },
  s08: {
    shot: { kind: "still", src: "s11_godown.png", zoom: [1.0, 1.1], origin: "30% 50%" },
    graphic: () => (
      <>
        <At left={1100} top={70}>
          <Panel title="Paid before the customer pays" enter={usePop(cue("s08", 0, 0.3))} width={740}>
            <ItemList
              size={28}
              items={[
                { icon: "📦", text: "Stock bought", at: cue("s08", 1, 0.02), color: PALETTE.red },
                { icon: "👥", text: "Staff paid", at: cue("s08", 1, 0.18), color: PALETTE.red },
                { icon: "🏬", text: "Godown rent", at: cue("s08", 1, 0.34), color: PALETTE.red },
                { icon: "⛽", text: "Trucks and diesel", at: cue("s08", 1, 0.55), color: PALETTE.red },
                { icon: "🧾", text: "Invoice goes out", at: cue("s08", 1, 0.85), color: PALETTE.navy },
              ]}
            />
          </Panel>
        </At>
        <Chip at={cue("s08", 2, 0.4)} color={PALETTE.green} left={1120} top={690}>…only then does the customer pay</Chip>
      </>
    ),
  },
  s09: {
    shot: { kind: "still", src: "s14_lata_desk.png", zoom: [1.0, 1.08], origin: "25% 40%" },
    graphic: () => (
      <At {...RIGHT}>
        <Panel enter={usePop(cue("s09", 0, 0.05))} width={800}>
          <GapBridge start={cue("s09", 0, 0.2)} gapAt={cue("s09", 0, 0.85)} />
        </Panel>
      </At>
    ),
  },
  s10: {
    shot: { kind: "still", src: "shot3_phone.png", zoom: [1.02, 1.1], origin: "25% 40%" },
    graphic: () => (
      <At {...RIGHT}>
        <Panel title="The journey of one rupee" enter={usePop(cue("s10", 0, 0.2))} width={800}>
          <RupeeTimeline
            lastDay={90}
            awayFrom={30}
            awayTo={90}
            awayAt={cue("s10", 4, 0.3)}
            stops={[
              { day: 1, label: "Stock bought on 30 days' credit", color: PALETTE.navy, at: cue("s10", 1, 0.2) },
              { day: 30, label: "Kapoor paid, goods go out", color: PALETTE.red, at: cue("s10", 2, 0.2) },
              { day: 90, label: "Sharma Retail pays", color: PALETTE.green, at: cue("s10", 3, 0.3) },
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s11: {
    shot: { kind: "still", src: "s04_lata_tablet.png", zoom: [1.04, 1.08], origin: "50% 45%" },
    dim: 0.72,
    graphic: () => (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingTop: 200 }}>
        <CycleLoop start={5} centre="…and again" />
      </AbsoluteFill>
    ),
  },
  s12: {
    shot: { kind: "still", src: "shot5_invoices.png", zoom: [1.0, 1.06], origin: "25% 45%" },
    graphic: () => (
      <At left={1000} top={90}>
        <Panel title="Where the ₹40 lakh comes from" tag="₹ LAKH · ILLUSTRATIVE" enter={usePop(cue("s12", 0, 0.3))} width={860}>
          <Waterfall
            max={60}
            start={0}
            width={790}
            height={400}
            steps={[
              { label: "With customers", value: 40, kind: "plus", color: PALETTE.orange, caption: "60 days of sales", at: cue("s12", 1, 0.3) },
              { label: "Extra stock", value: 15, kind: "plus", color: PALETTE.orange, caption: "one month", at: cue("s12", 2, 0.3) },
              { label: "Kapoor's credit", value: 15, kind: "minus", color: PALETTE.green, caption: "30 days", at: cue("s12", 3, 0.3) },
              { label: "Ramesh funds", value: 40, kind: "result", color: PALETTE.red, caption: "or his bank", at: cue("s12", 4, 0.3) },
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s13: {
    shot: { kind: "still", src: "s02_celebration.png", zoom: [1.0, 1.06], origin: "30% 40%" },
    graphic: () => (
      <>
        <At left={1100} top={90}>
          <Panel title="More sales mean more…" enter={usePop(cue("s13", 0, 0.6))} width={720}>
            <ItemList
              size={28}
              items={[
                { icon: "📦", text: "Stock", at: cue("s13", 1, 0.03), color: PALETTE.orange },
                { icon: "👥", text: "Staff", at: cue("s13", 1, 0.13), color: PALETTE.orange },
                { icon: "🚚", text: "Trucks on the road", at: cue("s13", 1, 0.25), color: PALETTE.orange },
                { icon: "🤝", text: "Credit given to customers", at: cue("s13", 1, 0.45), color: PALETTE.orange },
              ]}
            />
          </Panel>
        </At>
        <Chip at={cue("s13", 1, 0.75)} color={PALETTE.red} left={1120} top={640}>Spent long before it's received</Chip>
      </>
    ),
  },
  s14: {
    shot: { kind: "still", src: "s13b_bank_manager.jpg", zoom: [1.0, 1.07], origin: "35% 45%" },
    graphic: () => (
      <>
        <Chip at={cue("s14", 0, 0.5)} color={PALETTE.green} left={1120} top={150}>🏆 Biggest order ever</Chip>
        <Chip at={cue("s14", 0, 0.8)} color={PALETTE.navy} left={1120} top={240}>🏦 Asking for a higher limit</Chip>
        <At left={1100} top={380}>
          <Panel enter={usePop(cue("s14", 1))} width={720}>
            <div style={{ fontSize: 36, fontWeight: 700, color: PALETTE.muted }}>Not because the business was failing.</div>
            <div style={{ fontSize: 44, fontWeight: 900, color: PALETTE.green, marginTop: 8 }}>Because it was growing.</div>
          </Panel>
        </At>
      </>
    ),
  },
  s15: {
    shot: { kind: "still", src: "shot2_celebrate.png", zoom: [1.04, 1.1] },
    dim: 0.7,
    graphic: () => (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: 46, fontFamily: FONT }}>
        <BigLines size={60} lines={[{ text: "Working capital is made by decisions", color: "#fff", at: cue("s15", 0, 0.5) }]} />
        <Boxes
          width={330}
          items={[
            { title: "Sales", sub: "credit terms", color: PALETTE.green, at: cue("s15", 1, 0.45) },
            { title: "Purchase", sub: "how much stock", color: PALETTE.orange, at: cue("s15", 1, 0.57) },
            { title: "Dispatch", sub: "when invoices go", color: PALETTE.navy, at: cue("s15", 1, 0.69) },
            { title: "Collections", sub: "when cash comes", color: PALETTE.red, at: cue("s15", 1, 0.8) },
          ]}
        />
      </AbsoluteFill>
    ),
  },
  s16: {
    shot: { kind: "still", src: "s12_vikram_pitch.png", zoom: [1.0, 1.06], origin: "40% 40%" },
    graphic: () => (
      <>
        <Chip at={cue("s16", 0, 0.6)} color={PALETTE.navy} left={1300} top={110}>Credit: 60 → 90 days</Chip>
        <Chip at={cue("s16", 1, 0.65)} color={PALETTE.red} left={1300} top={200}>+₹20L waiting</Chip>
      </>
    ),
  },
  s17: {
    shot: { kind: "split", left: "s15_kapoor_call.png", right: "s18_ramesh_call.png" },
    graphic: () => (
      <At left={560} top={660}>
        <Panel enter={usePop(cue("s17", 1, 0.05))} width={800}>
          <SplitCompare
            start={cue("s17", 1, 0.1)}
            left={{ label: "2% discount saves", value: "₹0.9L", color: PALETTE.green }}
            right={{ label: "Extra on the shelves", value: "+₹30L", color: PALETTE.red }}
          />
        </Panel>
      </At>
    ),
  },
  s18: {
    shot: { kind: "still", src: "s11_godown.png", zoom: [1.1, 1.02], origin: "60% 50%" },
    graphic: () => <Chip at={cue("s18", 0, 0.25)} color={PALETTE.orange} left={1080} top={150}>🚚 A week late → invoice late → cash late</Chip>,
  },
  s19: {
    shot: { kind: "still", src: "s10_mehta_phone.png", zoom: [1.0, 1.08], origin: "25% 40%" },
    graphic: () => (
      <>
        <Chip at={cue("s19", 0, 0.75)} color={PALETTE.navy} left={1300} top={110}>Heard that before? (Episode 1)</Chip>
        <Chip at={cue("s19", 1, 0.6)} color={PALETTE.red} left={1300} top={200}>+₹15L waiting</Chip>
      </>
    ),
  },
  s20: {
    shot: { kind: "still", src: "shot3_phone.png", zoom: [1.1, 1.02], origin: "25% 40%" },
    graphic: () => (
      <At {...RIGHT}>
        <Panel title="Small decisions, added up" tag="₹ LAKH · ILLUSTRATIVE" enter={usePop(5)} width={800}>
          <Waterfall
            max={75}
            start={0}
            width={730}
            height={400}
            steps={[
              { label: "90-day credit", value: 20, kind: "plus", color: PALETTE.orange, caption: "Sales", at: 20 },
              { label: "3 months' stock", value: 30, kind: "plus", color: PALETTE.orange, caption: "Purchase", at: 42 },
              { label: "Mehta late", value: 15, kind: "plus", color: PALETTE.orange, caption: "Collections", at: 64 },
              { label: "More waiting", value: 65, kind: "result", color: PALETTE.red, caption: "plus the late truck", at: cue("s20", 0, 0.6) },
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s21: {
    shot: { kind: "stillThenClip", still: "s17_forecast.png", clip: "c17_forecast.mp4", clipSeconds: 8 },
    graphic: () => (
      <At left={1230} top={24}>
        <Panel title="Lata's Monday questions" enter={usePop(cue("s21", 0, 0.6))} width={660} padding="16px 22px">
          <ItemList
            size={22}
            items={[
              { icon: "⏱️", text: "How quickly are customers paying?", at: cue("s21", 1), color: PALETTE.navy },
              { icon: "📦", text: "How much stock are we carrying?", at: cue("s21", 2), color: PALETTE.navy },
              { icon: "🛒", text: "Are we buying more than we need?", at: cue("s21", 3), color: PALETTE.navy },
              { icon: "🔄", text: "How long does a rupee take to come back?", at: cue("s21", 4), color: PALETTE.navy },
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s22: {
    shot: { kind: "still", src: "s18_ramesh_call.png", zoom: [1.0, 1.06], origin: "45% 40%" },
    graphic: () => (
      <At left={1330} top={140}>
        <Panel title="Ramesh acts" enter={usePop(5)} width={560}>
          <ItemList
            size={26}
            items={[
              { icon: "🤝", text: "Hold at 60 days", at: cue("s22", 0, 0.4), color: PALETTE.green },
              { icon: "📦", text: "One month's stock, not three", at: cue("s22", 1, 0.5), color: PALETTE.green },
              { icon: "🏦", text: "Bank limit arranged early", at: cue("s22", 2, 0.3), color: PALETTE.green },
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s23: {
    shot: { kind: "still", src: "s21_calm_evening.png", zoom: [1.0, 1.06] },
    graphic: () => (
      <At left={0} top={50}>
        <div style={{ width: 1920 }}>
          <Boxes
            width={520}
            items={[
              { title: "Paid on time", sub: "three months later", color: PALETTE.green, at: cue("s23", 0, 0.2) },
              { title: "Limit used", sub: "but never stretched", color: PALETTE.navy, at: cue("s23", 0, 0.5) },
              { title: "Salaries", sub: "on the 1st, every month", color: PALETTE.orange, at: cue("s23", 0, 0.8) },
            ]}
          />
        </div>
      </At>
    ),
  },
  s24: {
    shot: { kind: "stage" },
    graphic: () => (
      <OfficeMitraMoment
        screen="demo-cfo-overdue-customers.png"
        caption="OfficeMitra · CFO pack · Top overdue customers and vendor exposure"
        points={["Read-only: never changes your books", "Tally · Zoho · any ERP export", "Runs on your own computer", "Who's overdue, what you owe suppliers"]}
      />
    ),
  },
  s25: {
    shot: { kind: "clip", src: "c21_calm_evening.mp4", seconds: 10, still: "s21_calm_evening.png" },
    graphic: () => (
      <At left={0} top={50}>
        <div style={{ width: 1920 }}>
          <Boxes
            width={860}
            items={[{ title: "Not idle money", sub: "the fuel between money spent and money received", color: PALETTE.orange, at: cue("s25", 0, 0.05) }]}
          />
        </div>
      </At>
    ),
  },
  s26: {
    shot: { kind: "still", src: "s21_calm_evening.png", zoom: [1.04, 1.1] },
    dim: 0.7,
    graphic: () => (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <BigLines
          size={84}
          lines={[
            { text: "Working capital is", color: "#fff", at: cue("s26", 0, 0.35) },
            { text: "the cost of keeping", color: PALETTE.orange, at: cue("s26", 0, 0.6) },
            { text: "the wheels turning.", color: PALETTE.orange, at: cue("s26", 0, 0.75) },
          ]}
        />
      </AbsoluteFill>
    ),
  },
  s27: {
    shot: { kind: "still", src: "s14_lata_desk.png", zoom: [1.08, 1.0], origin: "30% 45%" },
    graphic: () => (
      <At left={1080} top={130}>
        <Panel title="Try this this week" enter={usePop(10)} width={760}>
          <ItemList
            size={28}
            items={[
              { icon: "1️⃣", text: "Your top 5 customers", at: cue("s27", 0, 0.3), color: PALETTE.navy },
              { icon: "2️⃣", text: "Actual days to pay vs agreed", at: cue("s27", 0, 0.65), color: PALETTE.orange },
              { icon: "3️⃣", text: "Stock not moved in 90 days", at: cue("s27", 1, 0.4), color: PALETTE.red },
            ]}
          />
        </Panel>
      </At>
    ),
  },
  s28: { shot: { kind: "stage" }, graphic: () => <EndCard question="Where does your money wait the longest?" /> },
};

export const Episode002: React.FC = () => <Episode scenes={SCENES} art={SCENE_ART} />;
