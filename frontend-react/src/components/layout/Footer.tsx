export function Footer() {
  return (
    <footer className="bg-military-dark text-white mt-auto py-6">
      <div className="container mx-auto px-4 text-center">
        <p className="text-sm text-gray-300">
          &copy; {new Date().getFullYear()} Community Packing List. Mission-ready packing, simplified.
        </p>
      </div>
    </footer>
  );
}
