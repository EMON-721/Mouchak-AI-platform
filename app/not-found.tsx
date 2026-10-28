import Link from "next/link";
export default function NotFound() {
  return (
    <section className="page-width empty">
      <h1>পেজ পাওয়া যায়নি / Page not found</h1>
      <Link className="button dark" href="/explore">
        টুল খুঁজুন / Explore tools
      </Link>
    </section>
  );
}
