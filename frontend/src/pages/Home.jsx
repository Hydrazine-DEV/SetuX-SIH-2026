import GovernmentHeader from '../components/landing/GovernmentHeader';
import HeroSection from '../components/landing/HeroSection';
import PortalShowcase from '../components/landing/PortalShowcase';
import PlatformPillars from '../components/landing/PlatformPillars';
import StateImpact from '../components/landing/StateImpact';
import GovernmentFooter from '../components/landing/GovernmentFooter';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#F5F7FA] font-sans flex flex-col justify-between antialiased selection:bg-[#1769D2] selection:text-white">
      <GovernmentHeader />
      <main className="flex-grow">
        <HeroSection />
        <PortalShowcase />
        <PlatformPillars />
        <StateImpact />
      </main>
      <GovernmentFooter />
    </div>
  );
}
