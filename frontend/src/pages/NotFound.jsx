import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 sm:px-8 py-24">
      <p className="font-mono text-[11px] tracking-[0.18em] text-amber">404</p>
      <h1 className="mt-4 font-display text-3xl font-bold">
        This route is not on the network
      </h1>
      <Link to="/" className="mt-8 inline-block text-sm text-amber hover:underline">
        Return to landing
      </Link>
    </div>
  );
}
