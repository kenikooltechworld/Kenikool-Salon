import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CreditCardIcon, PackageIcon } from "@/components/icons";
import { formatCurrency } from "@/lib/utils/currency";

interface Service {
  id: string;
  name: string;
  duration: number;
  price: number;
  image_url?: string;
}

interface Product {
  id: string;
  name: string;
  quantity: number;
  price: number;
  image_url?: string;
}

interface ProductServiceTabsProps {
  services: Service[];
  products: Product[];
  onAddService: (service: Service) => void;
  onAddProduct: (product: Product) => void;
}

export function ProductServiceTabs({
  services,
  products,
  onAddService,
  onAddProduct,
}: ProductServiceTabsProps) {
  // Ensure services and products are always arrays
  const safeServices = Array.isArray(services) ? services : [];
  const safeProducts = Array.isArray(products) ? products : [];

  return (
    <Tabs defaultValue="services">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="services">
          <CreditCardIcon className="h-4 w-4 mr-2" />
          Services
        </TabsTrigger>
        <TabsTrigger value="products">
          <PackageIcon className="h-4 w-4 mr-2" />
          Products
        </TabsTrigger>
      </TabsList>

      <TabsContent value="services" className="space-y-2">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[500px] overflow-y-auto overflow-x-hidden p-2">
          {safeServices.map((service) => (
            <Card
              key={service.id}
              padding="none"
              className="cursor-pointer hover:shadow-[var(--shadow-lg)] hover:border-[var(--primary)] transition-all duration-200 group h-[140px] flex flex-col"
              onClick={() => onAddService(service)}
            >
              <CardContent className="p-0 flex flex-col overflow-hidden w-full h-full min-w-0">
                {service.image_url && (
                  <div className="w-full h-20 overflow-hidden bg-[var(--muted)] flex-shrink-0">
                    <img
                      src={service.image_url}
                      alt={service.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    />
                  </div>
                )}
                <div className="p-3 flex flex-col gap-1 flex-1 min-w-0 overflow-hidden">
                  <p className="font-semibold text-sm group-hover:text-[var(--primary)] transition-colors line-clamp-2 min-w-0">
                    {service.name}
                  </p>
                  <p className="text-xs text-[var(--muted-foreground)] truncate">
                    {service.duration} min
                  </p>
                  <p className="text-base font-bold text-[var(--primary)] truncate">
                    {formatCurrency(service.price)}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </TabsContent>

      <TabsContent value="products" className="space-y-2">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[500px] overflow-y-auto overflow-x-hidden p-2">
          {safeProducts.map((product) => (
            <Card
              key={product.id}
              padding="none"
              className={`cursor-pointer hover:shadow-[var(--shadow-lg)] hover:border-[var(--primary)] transition-all duration-200 group h-[140px] flex flex-col ${
                product.quantity <= 0 ? "opacity-50 cursor-not-allowed" : ""
              }`}
              onClick={() => onAddProduct(product)}
            >
              <CardContent className="p-0 flex flex-col overflow-hidden w-full h-full min-w-0">
                {product.image_url && (
                  <div className="w-full h-20 overflow-hidden bg-[var(--muted)] flex-shrink-0">
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    />
                  </div>
                )}
                <div className="p-3 flex flex-col gap-1 flex-1 min-w-0 overflow-hidden">
                  <p className="font-semibold text-sm group-hover:text-[var(--primary)] transition-colors line-clamp-2 min-w-0">
                    {product.name}
                  </p>
                  <p
                    className={`text-xs truncate ${
                      product.quantity <= 5
                        ? "text-[var(--destructive)] font-medium"
                        : "text-[var(--muted-foreground)]"
                    }`}
                  >
                    Stock: {product.quantity}
                  </p>
                  <p className="text-base font-bold text-[var(--primary)] truncate">
                    {formatCurrency(product.price)}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </TabsContent>
    </Tabs>
  );
}
