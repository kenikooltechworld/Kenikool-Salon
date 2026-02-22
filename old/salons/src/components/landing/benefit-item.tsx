import { CheckIcon } from "@/components/icons";

interface BenefitItemProps {
  title: string;
  description: string;
}

export function BenefitItem({ title, description }: BenefitItemProps) {
  return (
    <div className="flex gap-3">
      <CheckIcon size={24} className="text-[var(--success)] shrink-0 mt-1" />
      <div>
        <h3 className="font-semibold mb-1">{title}</h3>
        <p className="text-[var(--muted-foreground)]">{description}</p>
      </div>
    </div>
  );
}
