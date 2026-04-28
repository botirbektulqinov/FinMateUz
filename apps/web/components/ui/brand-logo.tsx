import Image from "next/image";

type BrandLogoProps = {
  size?: "sm" | "md" | "lg";
  showWordmark?: boolean;
  className?: string;
};

const sizes = {
  sm: "h-8 w-8",
  md: "h-10 w-10",
  lg: "h-12 w-12"
};

export function BrandLogo({ size = "md", showWordmark = false, className = "" }: BrandLogoProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`} aria-label="FinMate UZ">
      <span className={`${sizes[size]} relative shrink-0 overflow-hidden rounded-full shadow-sm ring-1 ring-line`}>
        <Image src="/brand-icon.png" alt="" fill sizes="48px" className="object-cover" priority={size === "lg"} />
      </span>
      {showWordmark ? (
        <span className="text-xl font-bold tracking-normal text-ink">
          FinMate<span className="text-[#079F83]">Uz</span>
        </span>
      ) : null}
    </div>
  );
}
