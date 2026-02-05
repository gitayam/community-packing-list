export function Footer() {
  return (
    <footer className="hidden md:block border-t border-dark-border py-6 mt-auto">
      <div className="container mx-auto px-4 text-center text-text-muted text-sm">
        <p>Community Packing List &copy; {new Date().getFullYear()}</p>
      </div>
    </footer>
  );
}
