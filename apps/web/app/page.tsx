export default function Home() {
  return (
    <main>
      <section className="hero">
        <p className="eyebrow">Adam</p>
        <h1>Western Canon Reader</h1>
        <p>
          This site will render Adam&apos;s trails, notes, and reading graph from the SQLite
          database in <code>packages/adam-agent/db/adam.db</code>.
        </p>
      </section>
    </main>
  );
}
