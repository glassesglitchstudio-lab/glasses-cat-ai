import { motion } from "framer-motion";

/**
 * Neon-Glass Kart Bileşeni
 * 
 * UI-PRO-MAX-ENGINE'nin amiral gemisi bileşeni.
 * Glassmorphism + Neon Orange + Spring Animasyon birleşimi.
 * 
 * Mühür: Admin (Berkay) - 2026-05-14
 */

const springTransition = {
  type: "spring",
  stiffness: 300,
  damping: 15,
  mass: 1,
};

const NeonGlassCard = ({
  title,
  subtitle,
  children,
  variant = "default", // default | neon | deep
  className = "",
  onClick,
}) => {
  const variants = {
    default:
      "glass hover:shadow-neon-orange-sm transition-shadow duration-300",
    neon: "glass-neon animate-neon-pulse",
    deep: "glass-deep",
  };

  return (
    <motion.div
      className={`
        relative p-8 rounded-2xl cursor-pointer
        ${variants[variant]}
        ${className}
      `}
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={springTransition}
      onClick={onClick}
    >
      {/* Neon üst çizgi */}
      <div className="absolute top-0 left-4 right-4 h-0.5 
        bg-gradient-to-r from-transparent via-neon-orange to-transparent" 
      />

      {/* İçerik */}
      <div className="relative z-10">
        {title && (
          <h3 className="text-xl font-bold text-white mb-1">{title}</h3>
        )}
        {subtitle && (
          <p className="text-sm text-gray-400 mb-4">{subtitle}</p>
        )}
        {children}
      </div>

      {/* Hover gradient overlay */}
      <div className="absolute inset-0 rounded-2xl 
        bg-gradient-to-b from-neon-orange/5 to-transparent 
        opacity-0 group-hover:opacity-100 
        transition-opacity duration-500 pointer-events-none" 
      />
    </motion.div>
  );
};

export default NeonGlassCard;

/**
 * KULLANIM:
 * 
 * import NeonGlassCard from "@/components/NeonGlassCard";
 * 
 * <NeonGlassCard 
 *   title="Hoş Geldin Admin" 
 *   subtitle="UI-PRO-MAX-ENGINE aktif"
 *   variant="neon"
 * >
 *   <p className="text-gray-300">İçerik buraya</p>
 * </NeonGlassCard>
 */
