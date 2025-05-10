import React from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Link } from 'react-router-dom';
import { ChevronRight, Database, BarChart2, Brain, Bot, Glasses } from 'lucide-react';
import FeatureCard from "../components/FeatureCard";
import ArticleCard from '../components/ArticleCard';
import GetStartedSection from '../components/GetStartedSection';
import SupportSection from '../components/SupportSection';
import ContactSection from '../components/ContactSection';

const Index = () => {
  return (
    <div className="min-h-screen bg-cover bg-center flex flex-col" style={{ backgroundImage: 'url("/0_2.jpg")' }}>
      <div className="flex flex-col items-center justify-center min-h-screen bg-[url('/background.jpg')] bg-cover bg-center text-center px-4">
        <div className="bg-white bg-opacity-90 p-8 rounded-lg shadow-lg mt-20">
          <h1 className="text-4xl font-bold mb-4">Welcome to Mithril</h1>
          <p className="text-xl mb-8">Your Comprehensive Data Platform Solution</p>
          <div className="space-y-4">
            <Button asChild className="w-full sm:w-auto">
              <Link to="/dashboard">Go to Dashboard</Link>
            </Button>
            <Button asChild variant="outline" className="w-full sm:w-auto">
              <Link to="/data-catalog">Explore Data Catalog</Link>
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-grow container mx-auto px-4 py-8 overflow-y-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">Welcome to Mithril: The allnex Data Platform</h2>
          <p className="text-xl text-gray-200 mb-4">
            Unleashing the Strength of Data for a Protected and Innovative Future
          </p>
          <p className="text-2xl font-semibold text-white mb-6">Discover. Protect. Innovate.</p>
          <p className="text-lg text-gray-200 mb-8">
            At allnex, we are dedicated to fostering a data-driven culture that empowers our teams to make informed decisions and drive innovation. Mithril is our advanced Data Platform, engineered with the resilience and protection synonymous with its name. Just as our coatings safeguard valuable assets, Mithril protects our data and intellectual property, guiding allnex into a future of new possibilities.
          </p>
          <Link to="/dashboard">
            <Button className="bg-orange-500 hover:bg-orange-600 text-white">
              Get Started with Mithril <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>

        <section className="mb-12">
          <h3 className="text-2xl font-bold text-white mb-6">Explore Our Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={<Database className="h-8 w-8 text-primary-500" />}
              title="Data Catalog"
              description="Access secure data repositories, understand data lineage, and collaborate with data stewards."
              link="/data-catalog"
            />
            <FeatureCard
              icon={<BarChart2 className="h-8 w-8 text-primary-500" />}
              title="Business Intelligence and Analytics"
              description="Leverage Power BI and Microsoft Fabric for insightful data analysis and standardized semantic models."
              link="/bi-analytics"
            />
            <FeatureCard
              icon={<Brain className="h-8 w-8 text-primary-500" />}
              title="Machine Learning and AI"
              description="Build predictive models, integrate with Azure AI Studio, and utilize user-friendly ML interfaces."
              link="/machine-learning-ai"
            />
            <FeatureCard
              icon={<Bot className="h-8 w-8 text-primary-500" />}
              title="AI Copilot"
              description="Interact with data through natural language queries and automate complex tasks."
              link="/ai-copilot"
            />
            <FeatureCard
              icon={<Glasses className="h-8 w-8 text-primary-500" />}
              title="Augmented Reality (AR) for Quality Enhancement"
              description="Visualize data analytics in real-time and improve quality control with AR."
              link="/ar-solutions"
            />
          </div>
        </section>

        <section className="mb-12">
          <h3 className="text-2xl font-bold text-white mb-6">Powered by Industry-Leading Technologies</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-white bg-opacity-90">
              <CardContent className="flex flex-col items-center p-6">
                <img src="/databricks-logo.png" alt="Databricks Logo" className="h-16 mb-4" />
                <h4 className="text-lg font-semibold mb-2">Databricks</h4>
                <p className="text-sm text-center">Unified analytics platform for big data processing and machine learning.</p>
              </CardContent>
            </Card>
            <Card className="bg-white bg-opacity-90">
              <CardContent className="flex flex-col items-center p-6">
                <img src="/microsoft-fabric-logo.png" alt="Microsoft Fabric Logo" className="h-16 mb-4" />
                <h4 className="text-lg font-semibold mb-2">Microsoft Fabric</h4>
                <p className="text-sm text-center">End-to-end analytics solution for data integration, warehousing, and business intelligence.</p>
              </CardContent>
            </Card>
            <Card className="bg-white bg-opacity-90">
              <CardContent className="flex flex-col items-center p-6">
                <img src="/azure-logo.png" alt="Microsoft Azure Logo" className="h-16 mb-4" />
                <h4 className="text-lg font-semibold mb-2">Microsoft Azure</h4>
                <p className="text-sm text-center">Cloud computing platform for building, testing, deploying, and managing applications and services.</p>
              </CardContent>
            </Card>
            <Card className="bg-white bg-opacity-90">
              <CardContent className="flex flex-col items-center p-6">
                <img src="/openai-logo.png" alt="OpenAI Logo" className="h-16 mb-4" />
                <h4 className="text-lg font-semibold mb-2">OpenAI/ChatGPT</h4>
                <p className="text-sm text-center">Advanced AI models for natural language processing and generation.</p>
              </CardContent>
            </Card>
          </div>
        </section>

        <section className="mb-12">
          <h3 className="text-2xl font-bold text-white mb-6">Stay Informed with Our Latest Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <ArticleCard
              title="Protecting Data Integrity with Purview"
              excerpt="Discover how our data governance frameworks safeguard our critical assets."
              link="/blog/data-integrity-purview"
            />
            <ArticleCard
              title="Innovating Manufacturing with Augmented Reality"
              excerpt="Learn how AR is transforming quality control and employee training."
              link="/blog/ar-in-manufacturing"
            />
            <ArticleCard
              title="Advancing with Predictive Analytics and Azure AI Studio"
              excerpt="Explore how predictive models and Azure AI Studio analytics are driving efficiency."
              link="/blog/predictive-analytics-azure-ai"
            />
          </div>
          <div className="text-center mt-6">
            <Link to="/blog">
              <Button variant="outline" className="text-white border-white hover:bg-white hover:text-blue-900">
                Read Our Blog
              </Button>
            </Link>
          </div>
        </section>

        <GetStartedSection />
        <SupportSection />
        <ContactSection />
      </div>
    </div>
  );
};

export default Index;
